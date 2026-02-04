"""
WhatsApp watcher for Silver Tier AI Employee.
Monitors WhatsApp Web for messages and creates action items in Needs_Action/ folder.

Features:
- Playwright browser automation for WhatsApp Web
- Persistent session management (QR code scan only once)
- Monitored contacts filter (monitors ALL messages from specified contacts)
- Urgent keyword detection for non-monitored contacts (urgent, help, asap, invoice, payment)
- Silver tier schema with approval workflow
- Graceful session expiration handling
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

from watchers.base_watcher import BaseWatcher
from utils.dedupe_state import DedupeTracker
from utils.frontmatter_utils import save_action_item
from models.action_item import ActionItemSchema, determine_risk_level, determine_priority

load_dotenv()

logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp watcher that monitors WhatsApp Web for messages.

    Extends BaseWatcher with WhatsApp-specific functionality:
    - Playwright browser automation
    - Persistent session management
    - Monitored contacts filter (monitors ALL messages from specified contacts)
    - Urgent keyword detection (for non-monitored contacts)
    - Action item creation with Silver schema
    """

    # Urgent keywords that trigger action item creation (only used when monitoring ALL contacts)
    # When monitoring specific contacts, ALL their messages are processed regardless of keywords
    URGENT_KEYWORDS = ['urgent', 'help', 'asap', 'invoice', 'payment', 'emergency', 'critical']

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize WhatsApp watcher.

        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        super().__init__(vault_path, check_interval)

        # Session directory for persistent browser context (not JSON file)
        session_dir = os.getenv('WHATSAPP_SESSION_DIR', '.whatsapp_session')
        self.session_dir = Path(session_dir)

        # Remote debugging port for MCP server to connect
        self.remote_debugging_port = int(os.getenv('WHATSAPP_CDP_PORT', '9222'))

        # Initialize deduplication tracker
        dedupe_file = os.getenv('WHATSAPP_DEDUPE_FILE', 'My_AI_Employee/.whatsapp_dedupe.json')
        self.dedupe_tracker = DedupeTracker(dedupe_file)

        # Browser components (initialized in _init_browser)
        self.playwright = None
        self.context: Optional[BrowserContext] = None  # Note: context is the browser for persistent mode
        self.page: Optional[Page] = None

        # Session state
        self.session_active = False
        self.last_session_check = None

        # Monitored contacts (loaded from Company_Handbook.md)
        self.monitored_contacts: List[str] = []
        self._load_monitored_contacts()

        self.logger.info("WhatsApp watcher initialized")
        self.logger.info(f"Session directory: {self.session_dir}")
        self.logger.info(f"Remote debugging port: {self.remote_debugging_port}")

    def _load_monitored_contacts(self) -> None:
        """
        Load list of monitored contacts from Company_Handbook.md.

        Looks for a section like:
        ## Monitored WhatsApp Contacts
        - Contact Name 1
        - Contact Name 2
        """
        try:
            handbook_path = self.vault_path / 'Company_Handbook.md'
            if not handbook_path.exists():
                self.logger.info("Company_Handbook.md not found, monitoring all contacts")
                return

            content = handbook_path.read_text(encoding='utf-8')

            # Look for monitored contacts section
            import re
            pattern = r'##\s*Monitored WhatsApp Contacts\s*\n((?:[-*]\s*.+\n)+)'
            match = re.search(pattern, content, re.IGNORECASE)

            if match:
                contacts_text = match.group(1)
                self.monitored_contacts = [
                    line.strip().lstrip('-*').strip()
                    for line in contacts_text.strip().split('\n')
                    if line.strip()
                ]
                self.logger.info(f"Monitoring {len(self.monitored_contacts)} specific contacts: {self.monitored_contacts}")
            else:
                self.logger.info("No monitored contacts section found, monitoring all contacts")

        except Exception as e:
            self.logger.error(f"Error loading monitored contacts: {e}")

    def _init_browser(self):
        """Initialize Playwright browser with persistent context and CDP remote debugging."""
        try:
            self.logger.info("Initializing Playwright browser for WhatsApp Web")
            self.logger.info(f"Using persistent session directory: {self.session_dir}")
            self.logger.info(f"Remote debugging port: {self.remote_debugging_port}")

            # Start Playwright
            self.playwright = sync_playwright().start()

            # Create session directory if it doesn't exist
            self.session_dir.mkdir(parents=True, exist_ok=True)

            # Launch persistent context (saves full browser profile automatically)
            # This is the "Host" in CDP architecture - opens remote debugging port
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=False,  # WhatsApp Web requires visible browser
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    f'--remote-debugging-port={self.remote_debugging_port}'  # CDP backdoor for MCP
                ],
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['notifications']
            )

            # Get or create page
            if len(self.context.pages) > 0:
                self.page = self.context.pages[0]
                self.logger.info("Reusing existing page from persistent context")
            else:
                self.page = self.context.new_page()
                self.logger.info("Created new page in persistent context")

            # Add extra JavaScript to hide automation
            self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            # Navigate to WhatsApp Web if not already there
            if self.page.url != 'https://web.whatsapp.com/':
                self.page.goto('https://web.whatsapp.com', timeout=60000)

            self.logger.info("Browser initialized successfully with persistent context")

        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}")
            self._close_browser()
            raise

    def _close_browser(self):
        """Close browser (session is saved automatically with persistent context)."""
        try:
            # With persistent context, session is saved automatically to session_dir
            # No need to manually call storage_state()

            if self.context:
                self.context.close()
                self.logger.info("Closed browser context (session saved automatically)")

            if self.playwright:
                self.playwright.stop()

        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

    def _check_session(self) -> bool:
        """
        Check if WhatsApp Web session is active.

        Returns:
            True if logged in, False if QR code scan needed
        """
        try:
            # Try multiple selectors to detect chat list (logged in state)
            selectors = [
                'div[aria-label="Chat list"]',
                'div[data-testid="chat-list"]',
                '#pane-side',
                'div[role="grid"]',
            ]

            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    self.session_active = True
                    self.logger.info("WhatsApp session is active")
                    return True
                except PlaywrightTimeoutError:
                    continue

            # If no chat list found, check for QR code
            try:
                self.page.wait_for_selector('canvas[aria-label*="Scan"]', timeout=5000)
                self.session_active = False
                self.logger.warning("WhatsApp session expired - QR code scan required")
                self._handle_session_expired()
                return False
            except PlaywrightTimeoutError:
                # Neither found - unknown state
                self.logger.error("Could not determine WhatsApp session state")
                return False

        except Exception as e:
            self.logger.error(f"Error checking session: {e}")
            return False

    def _handle_session_expired(self) -> None:
        """
        Handle session expiration by creating a notification action item.

        Creates an action item in Needs_Action/ to notify the user
        that WhatsApp session needs re-authentication.
        """
        try:
            self.logger.error("Creating session expiration notification")

            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            filename = f"{timestamp}_whatsapp_session_expired.md"
            file_path = self.needs_action / filename

            # Create notification content
            content = """# WhatsApp Session Expired - Re-authentication Required

## Issue

The WhatsApp Web session has expired and needs re-authentication.

## Steps to Fix

1. Stop the WhatsApp watcher
2. Run: `python My_AI_Employee/run_watcher.py --watcher whatsapp --init`
3. Scan the QR code with your phone
4. Restart the watcher

## Details

**Detected**: {date}
**Priority**: High (System notification)
**Risk Level**: Low

---

## Notes

This is an automated notification from the WhatsApp watcher. The session needs to be re-initialized before monitoring can continue.
""".format(date=datetime.now().isoformat())

            # Create minimal frontmatter for notification
            import frontmatter
            metadata = {
                'type': 'whatsapp',
                'received': datetime.now().isoformat(),
                'status': 'pending',
                'approval_required': False,
                'priority': 'High',
                'risk_level': 'Low',
                'action_type': 'notification',
                'sender': 'System',
                'subject': 'WhatsApp Session Expired'
            }

            post = frontmatter.Post(content, **metadata)
            save_action_item(post, file_path)

            self.logger.info(f"Created session expiration notification: {filename}")

        except Exception as e:
            self.logger.error(f"Error creating session expiration notification: {e}")

    def _save_session(self):
        """Save current session state."""
        try:
            if self.context and self.session_active:
                self.session_file.parent.mkdir(parents=True, exist_ok=True)
                self.context.storage_state(path=str(self.session_file))
                self.logger.debug("Session state saved")
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")

    def _load_session(self) -> bool:
        """
        Load saved session state.

        Returns:
            True if session loaded successfully, False otherwise
        """
        try:
            if self.session_file.exists():
                self.logger.info("Session file found, will load on browser init")
                return True
            else:
                self.logger.info("No saved session found")
                return False
        except Exception as e:
            self.logger.error(f"Error loading session: {e}")
            return False

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new messages.

        If monitored contacts are specified, returns ALL messages from those contacts.
        If no monitored contacts specified, returns only urgent messages.

        Returns:
            List of new message dictionaries with parsed content
        """
        try:
            # Fetch new messages from WhatsApp Web
            messages = self._fetch_new_messages()

            # Filter and deduplicate messages
            filtered_messages = []
            for msg in messages:
                # If monitoring specific contacts, accept ALL their messages
                # If monitoring all contacts, only accept urgent messages
                should_process = False

                if self.monitored_contacts:
                    # Monitored contacts mode: accept ALL messages from monitored contacts
                    should_process = True
                    self.logger.debug(f"Processing message from monitored contact: {msg.get('sender')}")
                else:
                    # All contacts mode: only accept urgent messages
                    should_process = self._detect_urgent_keywords(msg.get('body', ''))
                    if should_process:
                        self.logger.debug(f"Processing urgent message from: {msg.get('sender')}")

                if should_process:
                    msg_id = self._generate_message_id(msg)
                    if msg_id and not self.dedupe_tracker.is_processed(msg_id):
                        filtered_messages.append(msg)
                        self.dedupe_tracker.mark_processed(msg_id)

            if filtered_messages:
                self.logger.info(f"Found {len(filtered_messages)} new messages (after deduplication)")

            return filtered_messages

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return []

    def _fetch_new_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch new unread messages from WhatsApp Web by clicking into chats.

        This method clicks into chats with unread messages and reads ALL messages,
        providing full context. Messages will be marked as read by WhatsApp.

        Returns:
            List of message dictionaries with full message content
        """
        try:
            messages = []

            # Try multiple selectors for chat list (WhatsApp Web structure varies by region/language)
            chat_list_selectors = [
                'div[aria-label="Chat list"]',
                'div[aria-label*="chat"]',  # Partial match
                '#pane-side',
                'div[data-testid="chat-list"]',
                'div[role="grid"]',
                'div.chatlist',
                '[data-testid="chatlist"]'
            ]

            chat_list_elem = None
            working_selector = None

            for selector in chat_list_selectors:
                try:
                    self.logger.info(f"DEBUG: Trying chat list selector: {selector}")
                    self.page.wait_for_selector(selector, timeout=3000)
                    chat_list_elem = self.page.query_selector(selector)
                    if chat_list_elem:
                        working_selector = selector
                        self.logger.info(f"DEBUG: Found chat list with selector: {selector}")
                        break
                except Exception as e:
                    self.logger.debug(f"DEBUG: Selector '{selector}' failed: {e}")
                    continue

            if not chat_list_elem:
                self.logger.error("DEBUG: Could not find chat list with any selector!")
                # Take screenshot for debugging
                screenshot_path = Path('whatsapp_debug_screenshot.png')
                self.page.screenshot(path=str(screenshot_path))
                self.logger.error(f"DEBUG: Screenshot saved to {screenshot_path}")
                return []

            # Get all chat items - try multiple selectors
            chat_item_selectors = [
                f'{working_selector} div[role="listitem"]',
                'div[role="listitem"]',
                f'{working_selector} > div',  # Direct children
                f'{working_selector} div',     # Any descendant divs
                '[data-testid*="cell-frame"]',
                'div[data-testid="cell-frame-container"]',
                '[data-testid="chat"]',
                'div[class*="chat"]'
            ]

            chat_items = []
            for selector in chat_item_selectors:
                chat_items = self.page.query_selector_all(selector)
                if chat_items:
                    self.logger.info(f"DEBUG: Found {len(chat_items)} chats with selector: {selector}")
                    break

            if not chat_items:
                self.logger.error("DEBUG: Could not find any chat items!")

                # Let's inspect what's actually in the chat list
                self.logger.error("DEBUG: Inspecting chat list structure...")
                try:
                    # Get the HTML of the chat list to see what's inside
                    chat_list_html = self.page.evaluate(f'''
                        () => {{
                            const chatList = document.querySelector('{working_selector}');
                            if (chatList) {{
                                return {{
                                    childCount: chatList.children.length,
                                    firstChildTag: chatList.children[0]?.tagName,
                                    firstChildClass: chatList.children[0]?.className,
                                    firstChildRole: chatList.children[0]?.getAttribute('role'),
                                    firstChildTestId: chatList.children[0]?.getAttribute('data-testid')
                                }};
                            }}
                            return null;
                        }}
                    ''')
                    self.logger.error(f"DEBUG: Chat list structure: {chat_list_html}")
                except Exception as e:
                    self.logger.error(f"DEBUG: Error inspecting structure: {e}")

                screenshot_path = Path('whatsapp_debug_no_chats.png')
                self.page.screenshot(path=str(screenshot_path))
                self.logger.error(f"DEBUG: Screenshot saved to {screenshot_path}")
                return []

            self.logger.info(f"DEBUG: Found {len(chat_items)} total chats in chat list")

            # Process each chat item
            unread_count_found = 0
            for idx, chat in enumerate(chat_items[:20]):  # Limit to 20 most recent
                try:
                    # Get contact name first (for debugging)
                    contact_name_elem = chat.query_selector('span[dir="auto"][title]')
                    contact_name = contact_name_elem.get_attribute('title') if contact_name_elem else 'Unknown'

                    # Check for unread indicator - try multiple selectors
                    unread_badge = None
                    unread_selectors = [
                        'span[data-testid="icon-unread-count"]',
                        'span[aria-label*="unread"]',
                        'div[aria-label*="unread"]',
                        'span[data-icon="unread-count"]'
                    ]

                    for unread_selector in unread_selectors:
                        unread_badge = chat.query_selector(unread_selector)
                        if unread_badge:
                            self.logger.debug(f"DEBUG: Found unread badge with selector '{unread_selector}' for '{contact_name}'")
                            break

                    if not unread_badge:
                        self.logger.debug(f"DEBUG: Chat #{idx} '{contact_name}' - No unread badge found")
                        continue

                    unread_count_found += 1
                    self.logger.info(f"DEBUG: Chat #{idx} '{contact_name}' - HAS UNREAD BADGE!")

                    # Check if contact is monitored (if list specified)
                    if self.monitored_contacts and contact_name not in self.monitored_contacts:
                        self.logger.info(f"DEBUG: Skipping non-monitored contact: '{contact_name}' (not in {self.monitored_contacts})")
                        continue

                    # Log when we find a monitored contact
                    if self.monitored_contacts:
                        self.logger.info(f"Found unread messages from monitored contact: '{contact_name}'")

                    # Get unread count
                    unread_count_text = unread_badge.inner_text() or '1'
                    try:
                        unread_count = int(unread_count_text)
                    except ValueError:
                        unread_count = 1

                    self.logger.info(f"Clicking into chat '{contact_name}' to read {unread_count} message(s)")

                    # Click into the chat to read all messages
                    try:
                        chat.click()
                        time.sleep(2)  # Wait for chat to load

                        # Read all unread messages from the chat
                        chat_messages = self._read_chat_messages(contact_name, unread_count)

                        if chat_messages:
                            # Combine all messages into one body with full context
                            full_message_body = "\n\n".join([
                                f"[{msg['timestamp']}] {msg['body']}"
                                for msg in chat_messages
                            ])

                            messages.append({
                                'sender': contact_name,
                                'body': full_message_body,
                                'timestamp': chat_messages[-1]['timestamp'] if chat_messages else datetime.now().strftime('%H:%M'),
                                'date': datetime.now().isoformat(),
                                'unread_count': unread_count,
                                'message_count': len(chat_messages)
                            })

                            self.logger.info(f"Read {len(chat_messages)} message(s) from {contact_name}")

                        # Go back to chat list
                        self.page.keyboard.press('Escape')
                        time.sleep(1)

                    except Exception as e:
                        self.logger.error(f"Error reading chat for {contact_name}: {e}")
                        # Try to go back to chat list
                        try:
                            self.page.keyboard.press('Escape')
                            time.sleep(1)
                        except:
                            pass
                        continue

                except Exception as e:
                    self.logger.error(f"DEBUG: Error processing chat #{idx}: {e}")
                    continue

            self.logger.info(f"DEBUG SUMMARY: Total chats={len(chat_items)}, Chats with unread badge={unread_count_found}, Messages collected={len(messages)}")
            self.logger.info(f"Fetched {len(messages)} unread message previews from WhatsApp Web")

            # If no unread badges found at all, let's try alternative selectors
            if unread_count_found == 0:
                self.logger.warning("DEBUG: No unread badges found with 'icon-unread-count' selector")
                self.logger.warning("DEBUG: Trying alternative selectors...")

                # Try alternative unread indicators
                for idx, chat in enumerate(chat_items[:5]):  # Check first 5 chats
                    try:
                        contact_name_elem = chat.query_selector('span[dir="auto"][title]')
                        contact_name = contact_name_elem.get_attribute('title') if contact_name_elem else 'Unknown'

                        # Try different selectors for unread indicator
                        alt_selectors = [
                            'span[data-icon="unread-count"]',
                            'span[aria-label*="unread"]',
                            'div[aria-label*="unread"]',
                            'span.unread',
                            '[data-testid*="unread"]'
                        ]

                        for selector in alt_selectors:
                            elem = chat.query_selector(selector)
                            if elem:
                                self.logger.info(f"DEBUG: Found alternative unread indicator with '{selector}' for '{contact_name}'")
                                break
                    except Exception as e:
                        continue

            return messages

        except Exception as e:
            self.logger.error(f"Error fetching messages: {e}")
            return []

    def _read_chat_messages(self, contact_name: str, unread_count: int) -> List[Dict[str, str]]:
        """
        Read all messages from the currently open chat.

        Args:
            contact_name: Name of the contact
            unread_count: Number of unread messages

        Returns:
            List of message dictionaries with 'body' and 'timestamp'
        """
        messages = []

        try:
            # Wait for messages to load (increased wait time)
            time.sleep(3)

            # Find the message container - try multiple selectors
            message_container_selectors = [
                'div[data-testid="conversation-panel-messages"]',
                'div[data-testid="conversation-panel-body"]',
                'div[class*="message-list"]',
                'div[role="application"]',
                'div[data-testid="msg-container"]',
                '#main',
                'div[id="main"]',
                'div.copyable-area',
                'div[class*="copyable"]',
                'div[tabindex="-1"]'
            ]

            message_container = None
            self.logger.debug(f"Searching for message container with {len(message_container_selectors)} selectors...")

            for selector in message_container_selectors:
                try:
                    message_container = self.page.query_selector(selector)
                    if message_container:
                        self.logger.info(f"✓ Found message container with selector: {selector}")
                        break
                    else:
                        self.logger.debug(f"✗ Selector '{selector}' did not match")
                except Exception as e:
                    self.logger.debug(f"✗ Selector '{selector}' failed: {e}")

            if not message_container:
                self.logger.warning(f"Could not find message container for {contact_name} - tried {len(message_container_selectors)} selectors")
                self.logger.warning("Attempting to find messages directly on page...")
                # Try to find messages directly without container
                message_container = self.page

            # Get all message elements - try multiple selectors
            # We want incoming messages only (not our own sent messages)
            message_selectors = [
                'div[data-testid="msg-container"]',
                'div[class*="message-in"]',
                'div.message-in',
                'div[data-id]',
                'div[class*="message"]',
                'div.copyable-text',
                'span.selectable-text'
            ]

            all_message_elements = []
            self.logger.debug(f"Searching for message elements with {len(message_selectors)} selectors...")

            for selector in message_selectors:
                try:
                    elements = message_container.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        self.logger.info(f"✓ Found {len(elements)} message elements with selector: {selector}")
                        all_message_elements = elements
                        break
                    else:
                        self.logger.debug(f"✗ Selector '{selector}' found 0 elements")
                except Exception as e:
                    self.logger.debug(f"✗ Selector '{selector}' failed: {e}")

            if not all_message_elements:
                self.logger.warning(f"No message elements found with standard selectors")
                self.logger.warning("Trying to extract text content directly from page...")

                # Last resort: try to get any text content from the page
                try:
                    # Get all text content from the main area
                    text_content = self.page.inner_text('#main') if self.page.query_selector('#main') else ""
                    if text_content:
                        self.logger.info(f"Extracted {len(text_content)} characters of text from page")
                        # Create a single message with all text
                        messages.append({
                            'body': text_content.strip(),
                            'timestamp': datetime.now().strftime('%H:%M')
                        })
                        return messages
                except Exception as e:
                    self.logger.error(f"Failed to extract text content: {e}")

                return messages

            # Read only the unread messages (last N where N = unread_count)
            # Don't read old messages - only the new unread ones
            messages_to_read = min(len(all_message_elements), unread_count)
            recent_messages = all_message_elements[-messages_to_read:] if all_message_elements else []

            self.logger.info(f"Reading last {messages_to_read} unread message(s) from {contact_name} (total messages in chat: {len(all_message_elements)})")

            for msg_elem in recent_messages:
                try:
                    # Try to determine if this is an incoming message (not sent by us)
                    # Incoming messages typically have class "message-in" or similar
                    class_attr = msg_elem.get_attribute('class') or ''

                    # Skip outgoing messages (sent by us)
                    if 'message-out' in class_attr or 'msg-out' in class_attr:
                        continue

                    # Extract message text - try multiple selectors
                    text_selectors = [
                        'span.selectable-text',
                        'div.selectable-text',
                        'span[dir="ltr"]',
                        'div[class*="copyable-text"]',
                        'span[class*="selectable-text"]'
                    ]

                    message_text = None
                    for text_selector in text_selectors:
                        text_elem = msg_elem.query_selector(text_selector)
                        if text_elem:
                            message_text = text_elem.inner_text().strip()
                            if message_text:
                                break

                    if not message_text:
                        # Try getting all text content as fallback
                        message_text = msg_elem.inner_text().strip()

                    # Extract timestamp - try multiple selectors
                    timestamp_selectors = [
                        'span[data-testid="msg-time"]',
                        'div[data-testid="msg-meta"]',
                        'span[class*="time"]',
                        'div[class*="time"]'
                    ]

                    timestamp = None
                    for ts_selector in timestamp_selectors:
                        ts_elem = msg_elem.query_selector(ts_selector)
                        if ts_elem:
                            timestamp = ts_elem.inner_text().strip()
                            if timestamp:
                                break

                    if not timestamp:
                        timestamp = datetime.now().strftime('%H:%M')

                    # Only add if we have message text
                    if message_text and len(message_text) > 0:
                        messages.append({
                            'body': message_text,
                            'timestamp': timestamp
                        })
                        self.logger.debug(f"Read message: [{timestamp}] {message_text[:50]}...")

                except Exception as e:
                    self.logger.debug(f"Error reading individual message: {e}")
                    continue

            self.logger.info(f"Successfully read {len(messages)} message(s) from {contact_name}")
            return messages

        except Exception as e:
            self.logger.error(f"Error reading chat messages for {contact_name}: {e}")
            return messages

    def _detect_urgent_keywords(self, text: str) -> bool:
        """
        Detect if message contains urgent keywords.

        Args:
            text: Message text to check

        Returns:
            True if urgent keywords found, False otherwise
        """
        text_lower = text.lower()
        for keyword in self.URGENT_KEYWORDS:
            if keyword in text_lower:
                self.logger.debug(f"Urgent keyword detected: {keyword}")
                return True
        return False

    def _normalize_contact_identifier(self, contact_name: str) -> str:
        """
        Normalize contact identifier to handle phone number vs saved name variations.

        This ensures that "+92 313 3582607" and "Uneeza" are treated as the same contact
        for deduplication purposes.

        Args:
            contact_name: Contact name or phone number

        Returns:
            Normalized identifier (phone number if it looks like one, otherwise name)
        """
        # Remove all non-digit characters to check if it's a phone number
        digits_only = ''.join(c for c in contact_name if c.isdigit())

        # If it's mostly digits (phone number), use digits as normalized form
        if len(digits_only) >= 10:  # Typical phone number length
            return digits_only

        # Otherwise, use the name as-is (but lowercase for consistency)
        return contact_name.lower().strip()

    def _generate_message_id(self, message: Dict[str, Any]) -> str:
        """
        Generate unique ID for message deduplication.

        Uses normalized contact identifier to ensure phone numbers and saved names
        are treated as the same contact.

        Args:
            message: Message dictionary

        Returns:
            Unique message ID string
        """
        # Normalize sender to handle phone number vs name variations
        sender = message.get('sender', 'unknown')
        normalized_sender = self._normalize_contact_identifier(sender)

        # Use normalized sender + timestamp + hash of body
        timestamp = message.get('timestamp', '')
        body_preview = message.get('body', '')[:50]

        return f"{normalized_sender}_{timestamp}_{hash(body_preview)}"

    def _determine_priority(self, message: Dict[str, Any]) -> str:
        """
        Determine message priority based on content and unread count.

        Args:
            message: Message dictionary with 'body' and 'unread_count'

        Returns:
            Priority level: 'High', 'Medium', or 'Low'
        """
        body_lower = message.get('body', '').lower()
        unread_count = message.get('unread_count', 1)

        # High priority keywords
        high_keywords = ['urgent', 'asap', 'emergency', 'important', 'help', 'critical', 'invoice', 'payment']
        for keyword in high_keywords:
            if keyword in body_lower:
                return 'High'

        # Multiple messages might indicate urgency
        if unread_count >= 5:
            return 'High'
        elif unread_count >= 3:
            return 'Medium'

        # Default to Medium for WhatsApp messages (they're usually time-sensitive)
        return 'Medium'

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create action item file in Needs_Action/ folder.

        Args:
            item: Message item dictionary with content and metadata

        Returns:
            Path to created file, or None if creation failed
        """
        try:
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            sender_safe = item['sender'].replace(' ', '_').replace('/', '_')[:30]
            filename = f"{timestamp}_whatsapp_{sender_safe}.md"
            file_path = self.needs_action / filename

            # Determine risk level and priority
            risk_level = determine_risk_level('whatsapp', item)

            # Improved priority logic based on unread count and keywords
            priority = self._determine_priority(item)

            # Create ActionItemSchema
            action_item = ActionItemSchema(
                type='whatsapp',
                received=item['date'],
                status='pending',
                approval_required=True,  # WhatsApp messages require approval
                priority=priority,
                risk_level=risk_level,
                action_type='send_message',
                sender=item['sender'],
                subject=f"WhatsApp from {item['sender']}",
                body=item['body']
            )

            # Create markdown content
            unread_count = item.get('unread_count', 1)
            urgent_keywords = [kw for kw in self.URGENT_KEYWORDS if kw in item['body'].lower()]

            # Format message preview with proper line breaks
            message_preview = item['body'].replace('\r\n', '\n').replace('\r', '\n')

            content = f"""# WhatsApp Message from {item['sender']}

## Message Details

**From**: {item['sender']}
**Time**: {item.get('timestamp', 'Unknown')}
**Date**: {item.get('date', 'Unknown')}
**Unread Count**: {unread_count} message(s)
**Priority**: {priority}
**Risk Level**: {risk_level}

## Message Preview

{message_preview}

---

## Next Steps

- [ ] Read Company_Handbook.md for WhatsApp response guidelines
- [ ] Open WhatsApp Web to read full conversation
- [ ] Draft response based on handbook rules
- [ ] Create approval request in Pending_Approval/
- [ ] Wait for human approval
- [ ] Send message via browser_mcp server

## Notes

This WhatsApp message was detected by WhatsApp watcher and requires human approval before responding.

**Priority Reason**: {f"Urgent keywords detected: {', '.join(urgent_keywords)}" if urgent_keywords else f"{unread_count} unread message(s)"}

**WhatsApp Format Note**: When drafting a reply, use proper WhatsApp formatting:
- Keep messages concise and conversational
- Use line breaks for readability
- Avoid overly formal language (WhatsApp is more casual than email)
- Respond promptly to urgent messages (within 2 hours per Company Handbook)
"""

            # Save action item with frontmatter
            from dataclasses import asdict
            import frontmatter

            metadata = asdict(action_item)
            post = frontmatter.Post(content, **metadata)
            save_action_item(post, file_path)

            self.logger.info(f"Created WhatsApp action item: {filename} (priority: {priority})")
            return file_path

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise

    def run(self) -> None:
        """
        Run the WhatsApp watcher with polling loop.

        Monitors WhatsApp Web for urgent messages and creates action items.
        Handles session expiration gracefully.
        """
        self.logger.info(f"Starting WhatsApp watcher (check interval: {self.check_interval}s)")

        try:
            # Initialize browser
            self._init_browser()

            # Check session status
            if not self._check_session():
                self.logger.warning("=" * 60)
                self.logger.warning("WhatsApp session not active - QR code scan required")
                self.logger.warning("Please scan the QR code in the browser window")
                self.logger.warning("Waiting for QR code scan...")
                self.logger.warning("=" * 60)

                # Wait for user to scan QR code (max 5 minutes)
                for i in range(60):  # 60 attempts * 5 seconds = 5 minutes
                    time.sleep(5)
                    if self._check_session():
                        self.logger.info("QR code scanned successfully!")
                        self._save_session()
                        break
                else:
                    self.logger.error("QR code scan timeout - stopping watcher")
                    return

            # Main polling loop
            while True:
                try:
                    # Check session is still active
                    if not self._check_session():
                        self.logger.error("WhatsApp session expired")
                        self.logger.error("Stopping watcher - please restart and scan QR code")
                        break

                    # Check for updates
                    messages = self.check_for_updates()

                    # Create action items for urgent messages
                    for message in messages:
                        self.create_action_file(message)

                    # Save session periodically
                    self._save_session()

                except Exception as e:
                    self.logger.error(f"Error in WhatsApp watcher loop: {e}")
                    # Continue running despite errors (graceful degradation)

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("WhatsApp watcher stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error in WhatsApp watcher: {e}")
            raise
        finally:
            # Clean up browser
            self._close_browser()

    def initialize_session(self, timeout: int = 300000) -> bool:
        """
        Initialize WhatsApp Web session with QR code authentication.

        Opens a visible browser window for the user to scan the QR code.
        After successful login, saves the session for future use.

        Args:
            timeout: Maximum time in ms to wait for QR code scan (default: 5 minutes)

        Returns:
            True if session was successfully initialized

        Raises:
            TimeoutError: If QR code was not scanned within timeout
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting WhatsApp session initialization...")
        self.logger.info("A browser window will open. Please scan the QR code.")
        self.logger.info("=" * 60)

        try:
            # Initialize browser (headless=False for QR code scan)
            self._init_browser()

            # Wait for user to scan QR code
            self.logger.info("Waiting for QR code scan...")

            # Wait for chat list to appear (indicates successful login)
            # Try multiple selectors as WhatsApp Web structure can vary
            try:
                # Try multiple selectors in order of reliability
                selectors = [
                    'div[aria-label="Chat list"]',  # Most common
                    'div[data-testid="chat-list"]',  # Alternative
                    '#pane-side',  # Sidebar pane
                    'div[role="grid"]',  # Chat grid
                ]

                success = False
                for selector in selectors:
                    try:
                        self.logger.debug(f"Trying selector: {selector}")
                        self.page.wait_for_selector(selector, timeout=10000)
                        self.logger.info(f"Found chat list with selector: {selector}")
                        success = True
                        break
                    except PlaywrightTimeoutError:
                        continue

                if not success:
                    raise PlaywrightTimeoutError("Could not find chat list with any selector")

                # Mark session as active (needed for _save_session to work)
                self.session_active = True

                self.logger.info("=" * 60)
                self.logger.info("QR code scanned successfully!")
                self.logger.info("=" * 60)

                # Save session state
                self._save_session()
                self.logger.info(f"Session saved to: {self.session_file}")

                return True

            except PlaywrightTimeoutError:
                self.logger.error("QR code scan timeout - session initialization failed")
                return False

        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            raise
        finally:
            # Clean up browser
            self._close_browser()


def main():
    """CLI entry point for WhatsApp watcher."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='WhatsApp Watcher for Silver Tier Personal AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize WhatsApp session (first time setup)
  python -m watchers.whatsapp_watcher --init

  # Run watcher with existing session
  python -m watchers.whatsapp_watcher

  # Run watcher in headless mode (after session init)
  python -m watchers.whatsapp_watcher --headless
        """
    )
    parser.add_argument(
        '--init',
        action='store_true',
        help='Initialize WhatsApp session (scan QR code)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (requires existing session)'
    )
    parser.add_argument(
        '--vault-path',
        type=str,
        default='My_AI_Employee/AI_Employee_Vault',
        help='Path to Obsidian vault (default: My_AI_Employee/AI_Employee_Vault)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create watcher instance
    watcher = WhatsAppWatcher(
        vault_path=args.vault_path,
        check_interval=args.interval
    )

    if args.init:
        # Initialize session mode
        try:
            success = watcher.initialize_session()
            if success:
                print("\n" + "=" * 60)
                print("✓ Session initialized successfully!")
                print(f"✓ Session saved to: {watcher.session_file}")
                print("=" * 60)
                print("\nYou can now run the watcher with:")
                print(f"  python -m watchers.whatsapp_watcher --vault-path {args.vault_path}")
                sys.exit(0)
            else:
                print("\n✗ Failed to initialize session")
                sys.exit(1)
        except Exception as e:
            print(f"\n✗ Failed to initialize session: {e}")
            sys.exit(1)
    else:
        # Normal watcher mode
        if not watcher.session_file.exists():
            print("=" * 60)
            print("✗ WhatsApp session not found!")
            print("=" * 60)
            print("\nPlease initialize the session first:")
            print(f"  python -m watchers.whatsapp_watcher --init --vault-path {args.vault_path}")
            print("\nThis will open a browser window for QR code scanning.")
            sys.exit(1)

        try:
            watcher.run()
        except KeyboardInterrupt:
            print("\n\nShutting down WhatsApp watcher...")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()
