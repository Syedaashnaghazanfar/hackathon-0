"""
Gmail watcher for Silver Tier AI Employee.

Monitors Gmail inbox for new emails and creates action items in /Needs_Action/.
Uses Gmail API with OAuth2 authentication and deduplication via SHA256 hashing.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from googleapiclient.discovery import build

from my_ai_employee.watchers.api_base_watcher import APIBaseWatcher
from my_ai_employee.utils import (
    OAuth2Helper,
    compute_content_hash,
    write_markdown_with_frontmatter,
    log_action_item_created,
)
from my_ai_employee.models import WatcherStateSchema


class GmailWatcher(APIBaseWatcher):
    """
    Gmail watcher using Gmail API.

    Monitors inbox for new emails and creates structured action items.
    """

    def __init__(self, check_interval: int = 60):
        """
        Initialize Gmail watcher.

        Args:
            check_interval: Polling interval in seconds (default: 60)
        """
        super().__init__("gmail_watcher", check_interval)

        # Initialize OAuth2 helper
        self.oauth_helper = OAuth2Helper()

        # Initialize watcher state (for deduplication)
        self.state_file = Path(".gmail_dedupe.json")
        self.state = self._load_state()

        # Gmail API service
        self.service = None

    def _load_state(self) -> WatcherStateSchema:
        """Load watcher state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                return WatcherStateSchema.from_dict(data)
            except Exception as e:
                self.logger.warning(f"Failed to load state file, creating new: {e}")

        # Create new state
        return WatcherStateSchema(
            watcher_name="gmail",
            last_check=datetime.now(),
            health_status="healthy",
        )

    def _save_state(self) -> None:
        """Save watcher state to disk."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state file: {e}")

    def _initialize_service(self) -> None:
        """Initialize Gmail API service with OAuth2 credentials."""
        if self.service is not None:
            return

        try:
            credentials = self.oauth_helper.get_valid_credentials()
            self.service = build("gmail", "v1", credentials=credentials)
            self.logger.info("Gmail API service initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail API service: {e}")
            raise

    def check_for_new_items(self) -> None:
        """
        Check Gmail inbox for new emails.

        Fetches unread emails, creates action items for new ones.
        """
        try:
            # Initialize service if needed
            self._initialize_service()

            # Fetch unread emails
            messages = self._fetch_unread_emails()

            if not messages:
                self.logger.debug("No new emails found")
                return

            self.logger.info(f"Found {len(messages)} unread email(s)")

            # Process each email
            for message in messages:
                self._process_email(message)

            # Update state
            self.state.mark_success()
            self._save_state()

        except Exception as e:
            self.logger.error(f"Error checking for new emails: {e}", exc_info=True)
            self.state.mark_failure(str(e))
            self._save_state()

    def _fetch_unread_emails(self) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from Gmail inbox.

        Returns:
            List of email message dictionaries
        """
        try:
            # Query for unread emails in inbox
            results = self.service.users().messages().list(
                userId="me",
                q="is:unread in:inbox",
                maxResults=10,  # Limit to 10 newest
            ).execute()

            messages = results.get("messages", [])

            # Fetch full message details
            full_messages = []
            for msg in messages:
                msg_id = msg["id"]
                full_msg = self.service.users().messages().get(
                    userId="me",
                    id=msg_id,
                    format="full",
                ).execute()
                full_messages.append(full_msg)

            return full_messages

        except Exception as e:
            self.logger.error(f"Failed to fetch emails: {e}")
            return []

    def _process_email(self, message: Dict[str, Any]) -> None:
        """
        Process a single email message.

        Args:
            message: Gmail API message object
        """
        try:
            # Extract email details
            msg_id = message["id"]
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}

            sender = headers.get("From", "Unknown")
            subject = headers.get("Subject", "(No Subject)")
            date_str = headers.get("Date", "")

            # Extract body (simplified - get first text/plain part)
            body = self._extract_body(message["payload"])

            # Compute content hash for deduplication
            content_hash = compute_content_hash(
                f"{sender}{subject}{body}",
                {"date": date_str}
            )

            # Check if already processed
            if self.state.is_duplicate(content_hash):
                self.logger.debug(f"Skipping duplicate email: {subject}")
                return

            # Create action item
            action_item_path = self._create_action_item(
                msg_id=msg_id,
                sender=sender,
                subject=subject,
                body=body,
                date_str=date_str,
            )

            if action_item_path:
                # Mark as processed
                self.state.add_processed_hash(content_hash)
                log_action_item_created(self.logger, msg_id, "email", "auto")

                # Mark email as read (optional)
                if not self.config.dry_run:
                    self._mark_as_read(msg_id)

        except Exception as e:
            self.logger.error(f"Failed to process email: {e}", exc_info=True)

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from payload.

        Args:
            payload: Gmail API message payload

        Returns:
            Email body text
        """
        # Handle multipart messages
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body_data = part["body"].get("data", "")
                    if body_data:
                        import base64
                        return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")

        # Handle single-part messages
        body_data = payload.get("body", {}).get("data", "")
        if body_data:
            import base64
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")

        return "(No content)"

    def _create_action_item(
        self,
        msg_id: str,
        sender: str,
        subject: str,
        body: str,
        date_str: str,
    ) -> Path:
        """
        Create action item markdown file in /Needs_Action/.

        Args:
            msg_id: Gmail message ID
            sender: Email sender
            subject: Email subject
            body: Email body
            date_str: Email date string

        Returns:
            Path to created action item file
        """
        # Generate filename
        filename = self.create_action_item_filename(msg_id, "email")
        action_item_path = self.get_needs_action_path() / filename

        # Create frontmatter metadata
        metadata = {
            "type": "email",
            "received": datetime.now().isoformat(),
            "status": "pending",
            "priority": "auto",  # Will be auto-detected by ActionItemSchema
            "source_id": msg_id,
            "sender": sender,
            "subject": subject,
            "tags": ["email", "inbox"],
        }

        # Truncate body for preview
        content_preview = body[:2000] if len(body) > 2000 else body

        # Write action item
        write_markdown_with_frontmatter(action_item_path, metadata, content_preview)

        self.logger.info(f"Created action item: {filename}")
        return action_item_path

    def _mark_as_read(self, msg_id: str) -> None:
        """
        Mark email as read.

        Args:
            msg_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            self.logger.debug(f"Marked email {msg_id} as read")
        except Exception as e:
            self.logger.error(f"Failed to mark email as read: {e}")


def main():
    """Run Gmail watcher standalone."""
    watcher = GmailWatcher()
    watcher.run()


if __name__ == "__main__":
    main()
