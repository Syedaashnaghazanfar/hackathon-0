"""
WhatsApp watcher for Silver Tier AI Employee.

Monitors WhatsApp Web for new messages using Playwright browser automation
with session persistence to avoid repeated QR code scans.
"""

import json
import logging
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from my_ai_employee.config import get_config
from my_ai_employee.watchers.api_base_watcher import APIBaseWatcher
from my_ai_employee.utils import compute_content_hash, write_markdown_with_frontmatter, log_action_item_created
from my_ai_employee.models import WatcherStateSchema


class WhatsAppSessionExpiredError(Exception):
    """Raised when WhatsApp Web session has expired and needs re-authentication."""
    pass


class WhatsAppWatcher(APIBaseWatcher):
    """
    Watches WhatsApp Web for new messages and creates action items.

    Uses Playwright for browser automation with session persistence.
    The session is saved after QR code scan and reused for subsequent runs.

    Attributes:
        session_file: Path to the session storage JSON file.
        browser: Playwright browser instance.
        context: Browser context with session state.
        page: Active page for WhatsApp Web.
        headless: Whether to run browser in headless mode.
    """

    WHATSAPP_URL = 'https://web.whatsapp.com'
    QR_CODE_SELECTOR = 'canvas[aria-label="Scan this QR code to link a device!"]'
    CHAT_LIST_SELECTOR = 'div[aria-label="Chat list"]'
    UNREAD_BADGE_SELECTOR = 'span[data-testid="icon-unread-count"]'

    def __init__(self, check_interval: int = 60):
        """
        Initialize WhatsApp watcher.

        Args:
            check_interval: Polling interval in seconds (default: 60)
        """
        super().__init__("whatsapp_watcher", check_interval)

        # Get config
        config = get_config()
        self.session_file = Path(config.whatsapp_session_dir) / "session.json"
        self.headless = config.whatsapp_headless

        # Browser components
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None

        # Initialize watcher state (for deduplication)
        self.state_file = Path(".whatsapp_dedupe.json")
        self.state = self._load_state()

        # Needs action directory
        self.needs_action_dir = self.vault_path / "Needs_Action"

        self.logger.info(f"WhatsApp watcher initialized")
        self.logger.info(f"Session file: {self.session_file}")
        self.logger.info(f"Headless mode: {self.headless}")

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
        )

    def _save_state(self) -> None:
        """Save watcher state to disk."""
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state file: {e}")

    def initialize_session(self, timeout: int = 120000) -> bool:
        """
        Initialize WhatsApp Web session with QR code authentication.

        Opens a visible browser window for the user to scan the QR code.
        After successful login, saves the session for future use.

        Args:
            timeout: Maximum time in ms to wait for QR code scan.

        Returns:
            True if session was successfully initialized.

        Raises:
            TimeoutError: If QR code was not scanned within timeout.
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting WhatsApp session initialization...")
        self.logger.info("A browser window will open. Please scan the QR code.")
        self.logger.info("=" * 60)

        playwright = sync_playwright().start()

        try:
            # Launch visible browser for QR code scan
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to WhatsApp Web
            page.goto(self.WHATSAPP_URL)
            self.logger.info("Waiting for QR code scan...")

            # Wait for chat list to appear (indicates successful login)
            page.wait_for_selector(self.CHAT_LIST_SELECTOR, timeout=timeout)
            self.logger.info("✓ Login successful!")

            # Wait additional time to ensure session is fully established
            self.logger.info("Waiting for session to fully establish (10 seconds)...")
            page.wait_for_timeout(10000)  # Wait 10 seconds
            self.logger.info("✓ Session established")

            # Save session state
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            context.storage_state(path=str(self.session_file))
            self.logger.info(f"✓ Session saved to {self.session_file}")

            # Cleanup
            context.close()
            browser.close()
            playwright.stop()

            self.logger.info("=" * 60)
            self.logger.info("✓ WhatsApp session initialized successfully!")
            self.logger.info("You can now run the watcher in headless mode.")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            playwright.stop()
            raise

    def _ensure_browser(self) -> None:
        """
        Ensure browser is running with saved session.

        Raises:
            FileNotFoundError: If session file is missing.
            WhatsAppSessionExpiredError: If session has expired.
        """
        if self.page is not None:
            return

        if not self.session_file.exists():
            raise FileNotFoundError(
                f"WhatsApp session file not found: {self.session_file}\n"
                "Run 'uv run python src/my_ai_employee/watchers/whatsapp_watcher.py --init' to initialize."
            )

        self.logger.debug("Starting browser with saved session...")

        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            storage_state=str(self.session_file)
        )
        self.page = self.context.new_page()

        # Navigate to WhatsApp Web
        self.page.goto(self.WHATSAPP_URL)

        # Check for session expiration (QR code appears)
        if self._is_session_expired():
            self._handle_session_expired()
            raise WhatsAppSessionExpiredError(
                "WhatsApp session expired. Please re-scan QR code."
            )

        # Wait for chat list
        self.page.wait_for_selector(self.CHAT_LIST_SELECTOR, timeout=30000)
        self.logger.info("WhatsApp Web loaded successfully")

    def _is_session_expired(self) -> bool:
        """
        Check if the WhatsApp session has expired.

        Returns:
            True if QR code is displayed (session expired).
        """
        try:
            # Short timeout to check for QR code
            qr_element = self.page.query_selector(self.QR_CODE_SELECTOR)
            return qr_element is not None
        except Exception:
            return False

    def _handle_session_expired(self) -> None:
        """
        Handle session expiration by logging and cleaning up.
        """
        self.logger.error("WhatsApp session expired - QR code detected")
        self.logger.error("Please run: uv run python src/my_ai_employee/watchers/whatsapp_watcher.py --init")

        # Cleanup browser
        self._cleanup_browser()

    def _cleanup_browser(self) -> None:
        """Clean up browser resources."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            self.logger.error(f"Error cleaning up browser: {e}")
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self._playwright = None

    def check_for_new_items(self) -> None:
        """
        Check WhatsApp Web for new unread messages.

        Scans the chat list for unread messages and creates action items.
        """
        try:
            # Initialize browser if needed
            self._ensure_browser()

            # Get all chat items
            chat_items = self.page.locator(
                f'{self.CHAT_LIST_SELECTOR} div[role="listitem"]'
            ).all()

            new_messages = []

            for chat in chat_items:
                try:
                    # Check for unread indicator
                    unread_badge = chat.locator(self.UNREAD_BADGE_SELECTOR)
                    if unread_badge.count() == 0:
                        continue

                    # Get contact name
                    contact_name_elem = chat.locator('span[dir="auto"][title]').first
                    contact_name = contact_name_elem.get_attribute('title') or 'Unknown'

                    # Get unread count
                    unread_count_text = unread_badge.text_content() or '1'
                    try:
                        unread_count = int(unread_count_text)
                    except ValueError:
                        unread_count = 1

                    # Get last message preview
                    message_preview_elem = chat.locator('span[dir="ltr"]').last
                    message_preview = message_preview_elem.text_content() or ''

                    # Get timestamp
                    time_elem = chat.locator('div[class*="message-time"]')
                    timestamp = time_elem.text_content() if time_elem.count() > 0 else ''

                    # Generate unique ID for this message batch
                    msg_id = f"whatsapp-{contact_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    # Check if already processed
                    content_hash = compute_content_hash(f"{contact_name}:{message_preview}:{timestamp}")
                    if self.state.is_processed(content_hash):
                        continue

                    message_info = {
                        'id': msg_id,
                        'contact_name': contact_name,
                        'unread_count': unread_count,
                        'message_preview': message_preview[:200],
                        'timestamp': timestamp,
                        'detected_at': datetime.now(),
                        'content_hash': content_hash
                    }

                    new_messages.append(message_info)
                    self.logger.info(f"New message from: {contact_name} ({unread_count} unread)")

                except Exception as e:
                    self.logger.debug(f"Error processing chat item: {e}")
                    continue

            if new_messages:
                self.logger.info(f"Found {len(new_messages)} new WhatsApp message(s)")

                # Process each message
                for msg_info in new_messages:
                    self._process_message(msg_info)
                    # Mark as processed
                    self.state.mark_processed(msg_info['content_hash'])
                    self._save_state()

            else:
                self.logger.debug("No new WhatsApp messages found")

            # Update state
            self.state.mark_success()
            self._save_state()

        except WhatsAppSessionExpiredError:
            raise
        except Exception as e:
            self.logger.error(f"Error checking for new messages: {e}", exc_info=True)

            # Check if this is a session issue
            if self.page and self._is_session_expired():
                self._handle_session_expired()

            self.state.mark_failure(str(e))
            self._save_state()

    def _process_message(self, message_info: dict) -> None:
        """
        Create an action item file for a WhatsApp message.

        Args:
            message_info: Message info dict.
        """
        # Determine priority
        priority = self._determine_priority(message_info)

        # Create markdown content
        content = f"""# WhatsApp Message from {message_info['contact_name']}

**Contact:** {message_info['contact_name']}
**Unread Count:** {message_info['unread_count']}
**Time:** {message_info['timestamp']}

## Message Preview

{message_info['message_preview']}

---

*Open WhatsApp to see full conversation*
"""

        # Create action item
        action_item_path = self.needs_action_dir / f"{message_info['id']}.md"

        # Write using frontmatter
        write_markdown_with_frontmatter(
            path=action_item_path,
            content=content,
            frontmatter={
                'id': message_info['id'],
                'source': 'whatsapp',
                'type': 'message',
                'created': message_info['detected_at'].isoformat(),
                'priority': priority,
                'status': 'pending',
                'contact': message_info['contact_name'],
                'unread_count': message_info['unread_count'],
                'timestamp': message_info['timestamp'],
                'watcher_type': 'whatsapp'
            }
        )

        log_action_item_created(
            self.logger,
            message_info['id'],
            'whatsapp',
            priority
        )

    @staticmethod
    def _determine_priority(message_info: dict) -> str:
        """
        Determine message priority based on content and count.

        Args:
            message_info: Message info dict.

        Returns:
            Priority level: 'high', 'medium', or 'low'.
        """
        preview_lower = message_info.get('message_preview', '').lower()
        unread_count = message_info.get('unread_count', 1)

        # High priority keywords
        high_keywords = ['urgent', 'asap', 'emergency', 'important', 'help', 'critical']
        for keyword in high_keywords:
            if keyword in preview_lower:
                return 'high'

        # Multiple messages might indicate urgency
        if unread_count >= 5:
            return 'high'
        elif unread_count >= 3:
            return 'medium'

        return 'medium'

    def stop(self) -> None:
        """Stop the watcher and clean up browser resources."""
        self._cleanup_browser()
        super().stop()


def main():
    """CLI entry point for WhatsApp watcher."""
    parser = argparse.ArgumentParser(
        description='WhatsApp Watcher for Silver AI Employee'
    )
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize WhatsApp session (scan QR code)'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=None,
        help='Seconds between WhatsApp checks (overrides .env CHECK_INTERVAL)',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Enable verbose (debug) logging',
    )

    args = parser.parse_args()

    # Setup logging
    import logging
    from my_ai_employee.utils.logging_config import setup_logging

    setup_logging("whatsapp_watcher", log_level="DEBUG" if args.verbose else "INFO")
    logger = logging.getLogger(__name__)

    config = get_config()

    if args.init:
        # Initialize session mode
        watcher = WhatsAppWatcher(check_interval=config.check_interval)
        try:
            watcher.initialize_session()
            logger.info("Session initialized successfully!")
            logger.info(f"Session saved to: {watcher.session_file}")
            logger.info("")
            logger.info("Next steps:")
            logger.info("1. Start the watcher: uv run python src/my_ai_employee/watchers/whatsapp_watcher.py")
            logger.info("2. Or use PM2: pm2 start ecosystem.config.js")
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            sys.exit(1)
    else:
        # Run watcher mode
        watcher = WhatsAppWatcher(check_interval=args.check_interval or config.check_interval)

        try:
            watcher.run()
        except KeyboardInterrupt:
            logger.info("\nWatcher stopped by user")
            watcher.stop()
        except WhatsAppSessionExpiredError as e:
            logger.error(f"\n{e}")
            logger.error("Run with --init to re-authenticate")
            sys.exit(1)


if __name__ == '__main__':
    main()
