"""
WhatsApp watcher for Silver Tier AI Employee.

Monitors WhatsApp Web for new messages using Playwright browser automation.
Implements session persistence, urgent keyword detection, and deduplication.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from playwright.sync_api import sync_playwright, Browser, Page

from my_ai_employee.watchers.api_base_watcher import APIBaseWatcher
from my_ai_employee.utils import (
    compute_content_hash,
    write_markdown_with_frontmatter,
    log_action_item_created,
)
from my_ai_employee.models import WatcherStateSchema
from my_ai_employee.config import get_config


class WhatsAppWatcher(APIBaseWatcher):
    """
    WhatsApp watcher using Playwright browser automation.

    Monitors WhatsApp Web for new messages with urgent keyword detection.
    """

    # Urgent keywords for priority detection
    URGENT_KEYWORDS = [
        r"\binvoice\b",
        r"\bpayment\b",
        r"\bhelp\b",
        r"\burgent\b",
        r"\basap\b",
        r"\bemergency\b",
        r"\bcritical\b",
    ]

    def __init__(self, check_interval: int = 60):
        """
        Initialize WhatsApp watcher.

        Args:
            check_interval: Polling interval in seconds (default: 60)
        """
        super().__init__("whatsapp_watcher", check_interval)

        # Session directory
        self.session_dir = Path(self.config.whatsapp_session_dir)

        # Deduplication state
        self.state_file = Path(".whatsapp_dedupe.json")
        self.state = self._load_state()

        # Playwright browser (initialized on first check)
        self.playwright = None
        self.browser = None
        self.page = None

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
            watcher_name="whatsapp",
            last_check=datetime.now(),
            health_status="healthy",
            session_path=str(self.session_dir),
            session_authenticated=False,
        )

    def _save_state(self) -> None:
        """Save watcher state to disk."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state file: {e}")

    def _initialize_browser(self) -> None:
        """Initialize Playwright browser with persistent session."""
        if self.browser is not None:
            return

        try:
            self.playwright = sync_playwright().start()

            # Get config for headless mode
            config = get_config()

            # Launch browser with persistent context (loads saved session)
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=config.whatsapp_headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-web-security",
                ],
            )

            self.page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()

            # Navigate to WhatsApp Web
            self.page.goto("https://web.whatsapp.com", wait_until="networkidle")

            # Wait for chats to load (or QR code if not authenticated)
            # Try multiple selectors with 90 second timeout
            try:
                # Method 1: Check if we're on the main screen (not QR code)
                self.page.wait_for_selector("div[data-testid='panel']", timeout=90000)
                self.state.session_authenticated = True
                self.logger.info("WhatsApp Web session authenticated (found panel)")
            except:
                # Method 2: Try looking for chat list container
                try:
                    self.page.wait_for_selector("div[data-testid='chat']", timeout=10000)
                    self.state.session_authenticated = True
                    self.logger.info("WhatsApp Web session authenticated (found chat)")
                except:
                    # Method 3: Check if menu button exists (means we're logged in)
                    try:
                        self.page.wait_for_selector("div[data-testid='menu']", timeout=10000)
                        self.state.session_authenticated = True
                        self.logger.info("WhatsApp Web session authenticated (found menu)")
                    except:
                        self.state.session_authenticated = False
                        self.logger.warning("WhatsApp Web session not authenticated. Run setup script.")

            self._save_state()

        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise

    def check_for_new_items(self) -> None:
        """
        Check WhatsApp Web for new unread messages.

        Scans unread chats and creates action items for urgent messages.
        """
        try:
            # Initialize browser if needed
            self._initialize_browser()

            # Check if authenticated
            if not self.state.session_authenticated:
                self.logger.warning("Not authenticated. Skipping check.")
                return

            # Fetch unread messages
            messages = self._fetch_unread_messages()

            if not messages:
                self.logger.debug("No new WhatsApp messages found")
                return

            self.logger.info(f"Found {len(messages)} unread WhatsApp message(s)")

            # Process each message
            for message in messages:
                self._process_message(message)

            # Update state
            self.state.mark_success()
            self._save_state()

        except Exception as e:
            self.logger.error(f"Error checking for new messages: {e}", exc_info=True)
            self.state.mark_failure(str(e))
            self._save_state()

    def _fetch_unread_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch unread messages from WhatsApp Web.

        Returns:
            List of message dictionaries
        """
        messages = []

        try:
            # Find unread chats (chats with unread badge)
            unread_chats = self.page.query_selector_all("div[data-testid='cell-frame-container'] span[data-testid='icon-unread-count']")

            self.logger.debug(f"Found {len(unread_chats)} unread chat(s)")

            # Limit to first 5 unread chats
            for chat_badge in unread_chats[:5]:
                # Click on the chat
                chat_container = chat_badge.evaluate("(el) => el.closest('[data-testid=\"cell-frame-container\"]')")
                if chat_container:
                    self.page.click(f"[data-testid='cell-frame-container']:has-text('{chat_container}')")
                    self.page.wait_for_timeout(1000)  # Wait for chat to load

                    # Extract chat name
                    chat_name_elem = self.page.query_selector("div[data-testid='conversation-header'] span[dir='auto']")
                    chat_name = chat_name_elem.inner_text() if chat_name_elem else "Unknown"

                    # Extract last message
                    message_elems = self.page.query_selector_all("div[data-testid='msg-container']")
                    if message_elems:
                        last_message_elem = message_elems[-1]
                        message_text_elem = last_message_elem.query_selector("span.selectable-text")
                        message_text = message_text_elem.inner_text() if message_text_elem else ""

                        # Check if urgent
                        is_urgent = self._is_urgent(message_text)

                        messages.append({
                            "sender": chat_name,
                            "text": message_text,
                            "is_urgent": is_urgent,
                            "timestamp": datetime.now().isoformat(),
                        })

        except Exception as e:
            self.logger.error(f"Failed to fetch unread messages: {e}")

        return messages

    def _is_urgent(self, text: str) -> bool:
        """
        Check if message contains urgent keywords.

        Args:
            text: Message text

        Returns:
            True if urgent, False otherwise
        """
        text_lower = text.lower()
        for pattern in self.URGENT_KEYWORDS:
            if re.search(pattern, text_lower):
                return True
        return False

    def _process_message(self, message: Dict[str, Any]) -> None:
        """
        Process a single WhatsApp message.

        Args:
            message: Message dictionary
        """
        try:
            sender = message["sender"]
            text = message["text"]
            is_urgent = message["is_urgent"]

            # Compute content hash for deduplication
            content_hash = compute_content_hash(
                f"{sender}{text}",
                {"timestamp": message["timestamp"]}
            )

            # Check if already processed
            if self.state.is_duplicate(content_hash):
                self.logger.debug(f"Skipping duplicate message from {sender}")
                return

            # Create action item
            action_item_path = self._create_action_item(
                sender=sender,
                text=text,
                is_urgent=is_urgent,
                timestamp=message["timestamp"],
            )

            if action_item_path:
                # Mark as processed
                self.state.add_processed_hash(content_hash)
                priority = "high" if is_urgent else "medium"
                log_action_item_created(self.logger, content_hash[:8], "whatsapp", priority)

        except Exception as e:
            self.logger.error(f"Failed to process message: {e}", exc_info=True)

    def _create_action_item(
        self,
        sender: str,
        text: str,
        is_urgent: bool,
        timestamp: str,
    ) -> Path:
        """
        Create action item markdown file in /Needs_Action/.

        Args:
            sender: Message sender name
            text: Message text
            is_urgent: Whether message is urgent
            timestamp: Message timestamp

        Returns:
            Path to created action item file
        """
        # Generate filename
        safe_sender = "".join(c for c in sender if c.isalnum() or c in "-_")[:20]
        filename = self.create_action_item_filename(safe_sender, "whatsapp")
        action_item_path = self.get_needs_action_path() / filename

        # Create frontmatter metadata
        priority = "high" if is_urgent else "medium"
        metadata = {
            "type": "whatsapp",
            "received": timestamp,
            "status": "pending",
            "priority": priority,
            "source_id": f"whatsapp-{safe_sender}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "sender": sender,
            "subject": f"WhatsApp message from {sender}",
            "tags": ["whatsapp", "urgent"] if is_urgent else ["whatsapp"],
        }

        # Write action item
        write_markdown_with_frontmatter(action_item_path, metadata, text)

        self.logger.info(f"Created action item: {filename} (urgent={is_urgent})")
        return action_item_path

    def stop(self) -> None:
        """Stop the watcher and close browser."""
        super().stop()

        # Close browser
        if self.browser:
            try:
                self.browser.close()
                self.logger.info("Browser closed")
            except:
                pass

        # Stop playwright
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass


def main():
    """Run WhatsApp watcher standalone."""
    watcher = WhatsAppWatcher()
    watcher.run()


if __name__ == "__main__":
    main()
