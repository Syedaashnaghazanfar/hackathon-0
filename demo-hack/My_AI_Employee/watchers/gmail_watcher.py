"""
Gmail watcher for Silver Tier AI Employee.
Monitors Gmail inbox for new emails and creates action items in Needs_Action/ folder.

Features:
- OAuth2 authentication with automatic token refresh
- Deduplication to prevent duplicate action items
- Priority and risk level detection
- Silver tier schema with approval workflow
"""

import os
import sys
import time
import base64
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from watchers.base_watcher import BaseWatcher
from utils.auth_helper import OAuth2Helper, load_auth_from_env
from utils.dedupe_state import DedupeTracker
from utils.frontmatter_utils import save_action_item
from models.action_item import ActionItemSchema, determine_risk_level, determine_priority

load_dotenv()

logger = logging.getLogger(__name__)


class GmailWatcher(BaseWatcher):
    """
    Gmail watcher that monitors inbox for new emails.

    Extends BaseWatcher with Gmail-specific functionality:
    - OAuth2 authentication via OAuth2Helper
    - Gmail API integration for message fetching
    - Deduplication using Gmail message IDs
    - Action item creation with Silver schema
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize Gmail watcher.

        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        super().__init__(vault_path, check_interval)

        # Load OAuth2 configuration from environment
        auth_config = load_auth_from_env()

        # Initialize OAuth2 helper
        self.oauth_helper = OAuth2Helper(
            credentials_file=auth_config['credentials_file'],
            token_file=auth_config['token_file'],
            scopes=auth_config['scopes']
        )

        # Build Gmail service
        try:
            self.service = self.oauth_helper.build_service('gmail', 'v1')
            self.logger.info("Gmail service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail service: {e}")
            raise

        # Initialize deduplication tracker
        dedupe_file = os.getenv('GMAIL_DEDUPE_FILE', 'My_AI_Employee/.gmail_dedupe.json')
        self.dedupe_tracker = DedupeTracker(dedupe_file)

        # Track last check time for incremental fetching
        self.last_check_time = None

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail inbox for new messages.

        Returns:
            List of new message dictionaries with parsed content
        """
        try:
            # Fetch new messages from Gmail
            messages = self._fetch_new_messages()

            # Filter out duplicates
            new_messages = []
            for msg in messages:
                msg_id = msg.get('id')
                if msg_id and not self.dedupe_tracker.is_processed(msg_id):
                    new_messages.append(msg)
                    self.dedupe_tracker.mark_processed(msg_id)

            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new messages (after deduplication)")

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking for Gmail updates: {e}")
            return []

    def _fetch_new_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch new messages from Gmail API.

        Returns:
            List of message dictionaries with full content

        Raises:
            HttpError: If Gmail API returns an error
        """
        try:
            # Build query for unread messages in inbox
            query = 'is:unread in:inbox'

            self.logger.debug(f"Fetching messages with query: {query}")

            # List messages
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                q=query,
                maxResults=10  # Limit to 10 messages per check
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                self.logger.debug("No unread messages in inbox")
                return []

            self.logger.info(f"Found {len(messages)} unread message(s) to process")

            # Fetch full content for each message
            full_messages = []
            for msg in messages:
                try:
                    full_msg = self._get_message_details(msg['id'])
                    if full_msg:
                        full_messages.append(full_msg)
                        self.logger.debug(f"Fetched message: {full_msg.get('subject', 'No subject')[:50]}")
                except HttpError as e:
                    self.logger.error(f"Failed to fetch message {msg['id']}: {e}")
                    continue
                except Exception as e:
                    self.logger.error(f"Unexpected error fetching message {msg['id']}: {e}")
                    continue

            return full_messages

        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")

            # Handle specific HTTP error codes
            if e.resp.status == 401:
                self.logger.error(
                    "Authentication expired. Please delete token.json and re-authenticate.\n"
                    "Run: rm My_AI_Employee/token.json && uv run python setup_gmail_oauth_oob.py"
                )
            elif e.resp.status == 403:
                self.logger.error(
                    "Permission denied. Check that Gmail API is enabled in Google Cloud Console.\n"
                    "Visit: https://console.cloud.google.com/apis/library/gmail.googleapis.com"
                )
            elif e.resp.status == 429:
                self.logger.error("Rate limit exceeded. Waiting before retry...")
                time.sleep(60)  # Wait 1 minute before retry
            elif e.resp.status >= 500:
                self.logger.error("Gmail API server error. Will retry on next check.")

            # Attempt token refresh for auth errors
            if e.resp.status == 401:
                self.logger.info("Attempting to refresh OAuth token...")
                try:
                    self.oauth_helper.get_credentials()  # This will auto-refresh
                    self.service = self.oauth_helper.build_service('gmail', 'v1')
                    self.logger.info("Token refreshed successfully")
                except Exception as refresh_error:
                    self.logger.error(f"Failed to refresh token: {refresh_error}")

            return []

        except Exception as e:
            self.logger.error(f"Unexpected error fetching Gmail messages: {e}")
            return []

    def _get_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details for a specific message.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with message details (id, sender, subject, body, timestamp)
        """
        try:
            # Get message with full format
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = message['payload'].get('headers', [])
            sender = self._get_header_value(headers, 'From')
            subject = self._get_header_value(headers, 'Subject')
            date = self._get_header_value(headers, 'Date')

            # Extract body
            body = self._extract_body(message['payload'])

            # Get internal date (epoch ms)
            internal_date = message.get('internalDate')
            timestamp = datetime.fromtimestamp(int(internal_date) / 1000).isoformat() + 'Z' if internal_date else datetime.utcnow().isoformat() + 'Z'

            return {
                'id': message_id,
                'sender': sender,
                'subject': subject,
                'body': body,
                'date': date,
                'timestamp': timestamp,
                'labels': message.get('labelIds', [])
            }

        except Exception as e:
            self.logger.error(f"Error getting message details for {message_id}: {e}")
            return None

    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """
        Extract header value by name.

        Args:
            headers: List of header dictionaries
            name: Header name to find

        Returns:
            Header value or empty string
        """
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value', '')
        return ''

    def _extract_body(self, payload: Dict) -> str:
        """
        Extract email body from message payload.

        Args:
            payload: Message payload from Gmail API

        Returns:
            Decoded email body text
        """
        try:
            # Check if body is in the main payload
            if 'body' in payload and 'data' in payload['body']:
                return self._decode_body(payload['body']['data'])

            # Check if body is in parts (multipart message)
            if 'parts' in payload:
                for part in payload['parts']:
                    # Look for text/plain or text/html
                    mime_type = part.get('mimeType', '')
                    if 'text/plain' in mime_type or 'text/html' in mime_type:
                        if 'data' in part.get('body', {}):
                            return self._decode_body(part['body']['data'])

                    # Recursively check nested parts
                    if 'parts' in part:
                        body = self._extract_body(part)
                        if body:
                            return body

            return ''

        except Exception as e:
            self.logger.error(f"Error extracting body: {e}")
            return ''

    def _decode_body(self, data: str) -> str:
        """
        Decode base64url encoded body data.

        Args:
            data: Base64url encoded string

        Returns:
            Decoded text
        """
        try:
            # Gmail uses base64url encoding (RFC 4648)
            decoded_bytes = base64.urlsafe_b64decode(data)
            return decoded_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            self.logger.error(f"Error decoding body: {e}")
            return ''

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create action item file in Needs_Action/ folder.

        Args:
            item: Message dictionary with parsed content

        Returns:
            Path to created action item file, or None if creation failed

        Raises:
            Exception: If action file creation fails
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            sender_clean = item['sender'].split('<')[0].strip().replace(' ', '_')[:30]
            filename = f"{timestamp}_email_{sender_clean}.md"
            file_path = self.needs_action / filename

            self.logger.debug(f"Creating action file: {filename}")

            # Determine risk level and priority
            risk_level = determine_risk_level('send_email', item)

            # Check for urgent keywords in subject/body
            urgent_keywords = []
            text_to_check = f"{item.get('subject', '')} {item.get('body', '')}".lower()
            for keyword in ['urgent', 'asap', 'emergency', 'critical', 'immediate']:
                if keyword in text_to_check:
                    urgent_keywords.append(keyword)

            # Improved priority detection with sender and subject
            priority = determine_priority(
                risk_level=risk_level,
                urgency_keywords=urgent_keywords,
                sender=item.get('sender', ''),
                subject=item.get('subject', '')
            )

            self.logger.debug(
                f"Email analysis: priority={priority}, risk={risk_level}, "
                f"urgent_keywords={urgent_keywords}"
            )

            # Create action item with Silver schema
            action_item = ActionItemSchema(
                type='email',
                received=item['timestamp'],
                status='pending',
                approval_required=True,  # All emails require approval
                priority=priority,
                risk_level=risk_level,
                action_type='send_email',
                sender=item['sender'],
                subject=item['subject'],
                body=item['body'][:1000]  # Limit body length in frontmatter
            )

            # Format email body with proper line breaks
            email_body = item['body'].replace('\r\n', '\n').replace('\r', '\n')

            # Create markdown content
            content = f"""# Email from {item['sender']}

## Details

**From**: {item['sender']}
**Subject**: {item['subject']}
**Date**: {item.get('date', 'Unknown')}
**Priority**: {priority}
**Risk Level**: {risk_level}

## Message Body

{email_body}

---

## Next Steps

- [ ] Read Company_Handbook.md for email response guidelines
- [ ] Draft response based on handbook rules
- [ ] Create approval request in Pending_Approval/
- [ ] Wait for human approval
- [ ] Send email via email_mcp server

## Notes

This email was detected by Gmail watcher and requires human approval before responding.

**Email Format Note**: When drafting a reply, use proper email formatting:
- Start with a greeting (e.g., "Hello [Name],")
- Use paragraphs separated by blank lines
- End with a closing (e.g., "Best regards,")
- Include signature if appropriate
"""

            # Save action item with frontmatter
            # Convert ActionItemSchema to dict for frontmatter
            from dataclasses import asdict
            import frontmatter

            metadata = asdict(action_item)
            post = frontmatter.Post(content, **metadata)
            save_action_item(post, file_path)

            self.logger.info(f"Created action item: {filename} (priority: {priority})")
            return file_path

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise

    def _generate_message_id(self, item: Dict[str, Any]) -> str:
        """
        Generate stable ID for deduplication.

        Args:
            item: Message dictionary

        Returns:
            Stable message ID (Gmail message ID)
        """
        return item.get('id', '')


def main():
    """Main entry point for Gmail watcher."""
    # Load configuration
    vault_path = os.getenv('VAULT_PATH', 'My_AI_Employee/AI_Employee_Vault')
    check_interval = int(os.getenv('GMAIL_CHECK_INTERVAL', '60'))

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create and run watcher
    watcher = GmailWatcher(vault_path, check_interval)

    try:
        watcher.run()
    except KeyboardInterrupt:
        logger.info("Gmail watcher stopped by user")
    except Exception as e:
        logger.error(f"Gmail watcher crashed: {e}")
        raise


if __name__ == '__main__':
    main()
