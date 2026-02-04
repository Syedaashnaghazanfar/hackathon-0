#!/usr/bin/env python3
"""
Browser MCP Server - Send WhatsApp messages via browser automation.

Uses Playwright for browser automation to:
1. Authenticate with WhatsApp Web (persistent session)
2. Send messages to contacts
3. Handle session management and health checks

Type-safe with Pydantic v2 models for validation.
Integrated with AuditLogger for Silver tier compliance.
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel, Field, field_validator
from fastmcp import FastMCP
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
import asyncio

from utils.audit_logger import AuditLogger

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="browser-mcp")

# Initialize audit logger
vault_root = os.getenv('VAULT_ROOT', 'My_AI_Employee/AI_Employee_Vault')
audit_logger = AuditLogger(vault_root)

# Session storage - using persistent context directory (not JSON file)
SESSION_DIR = os.getenv('WHATSAPP_SESSION_DIR', '.whatsapp_session')
CDP_PORT = int(os.getenv('WHATSAPP_CDP_PORT', '9222'))


# ============================================================================
# PYDANTIC MODELS - Type-safe WhatsApp message validation
# ============================================================================

class WhatsAppMessageRequest(BaseModel):
    """WhatsApp message request model with validation."""

    contact: str = Field(..., description="Contact name or phone number")
    message: str = Field(..., description="Message text to send")

    @field_validator('contact')
    @classmethod
    def validate_contact(cls, v):
        """Contact cannot be empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Contact cannot be empty')
        return v

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Message cannot be empty and must be reasonable length."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message too long (max 5000 characters)')
        return v


class WhatsAppMessageResponse(BaseModel):
    """WhatsApp message response model."""

    success: bool = Field(..., description="Whether message was sent successfully")
    message_id: str = Field(default="", description="Message ID (timestamp-based)")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# ============================================================================
# WHATSAPP BROWSER AUTOMATION
# ============================================================================

class WhatsAppBrowser:
    """WhatsApp Web browser automation using Playwright with CDP connection."""

    def __init__(self):
        """Initialize WhatsApp browser."""
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.session_dir = Path(SESSION_DIR)
        self.cdp_port = CDP_PORT
        self.connected_via_cdp = False  # Track if we connected to existing browser

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start browser by connecting to watcher's CDP or launching fallback."""
        try:
            self.playwright = await async_playwright().start()

            # STRATEGY 1: Try to connect to watcher's browser via CDP (Guest mode)
            try:
                logger.info(f"Attempting to connect to watcher's browser via CDP on port {self.cdp_port}")
                self.browser = await self.playwright.chromium.connect_over_cdp(
                    f'http://localhost:{self.cdp_port}'
                )

                # Get the existing context and page from watcher's browser
                if len(self.browser.contexts) > 0:
                    self.context = self.browser.contexts[0]
                    if len(self.context.pages) > 0:
                        self.page = self.context.pages[0]
                        self.connected_via_cdp = True
                        logger.info("Successfully connected to watcher's browser via CDP")
                        return
                    else:
                        logger.warning("Connected via CDP but no pages found")
                else:
                    logger.warning("Connected via CDP but no contexts found")

                # If we got here, CDP connection didn't work properly
                await self.browser.close()
                self.browser = None

            except Exception as cdp_error:
                logger.warning(f"CDP connection failed: {cdp_error}")
                logger.info("Falling back to launching own browser instance")

            # STRATEGY 2: Fallback - Launch our own persistent context (Host mode)
            # This happens if watcher is not running
            logger.info("Launching fallback browser with persistent context")
            self.session_dir.mkdir(parents=True, exist_ok=True)

            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=False,  # WhatsApp Web requires visible browser
                args=[
                    '--disable-blink-features=AutomationControlled',
                    f'--remote-debugging-port={self.cdp_port}'
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
            else:
                self.page = await self.context.new_page()

            self.connected_via_cdp = False
            logger.info("Fallback browser started successfully")

        except Exception as e:
            logger.error(f"Error starting WhatsApp browser: {e}")
            await self.close()
            raise

    async def close(self):
        """Close browser (only if we launched it, not if connected via CDP)."""
        try:
            if self.connected_via_cdp:
                # We connected to watcher's browser - just disconnect, don't close
                logger.info("Disconnecting from watcher's browser (not closing)")
                if self.browser:
                    await self.browser.close()  # This just disconnects the CDP connection
            else:
                # We launched our own browser - close it properly
                if self.context:
                    await self.context.close()
                    logger.info("Closed fallback browser (session saved automatically)")

            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.error(f"Error closing WhatsApp browser: {e}")

    async def is_logged_in(self) -> bool:
        """Check if user is logged into WhatsApp Web."""
        try:
            # If connected via CDP, page is already on WhatsApp Web - don't navigate
            if not self.connected_via_cdp:
                await self.page.goto('https://web.whatsapp.com', timeout=30000)
            else:
                logger.info("Connected via CDP - using existing page")

            # Wait for either QR code or chat list
            try:
                # If we see the chat list, we're logged in
                await self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=10000)
                logger.info("WhatsApp session is valid")
                return True
            except PlaywrightTimeoutError:
                # Try alternative selector
                try:
                    await self.page.wait_for_selector('div[aria-label="Chat list"]', timeout=5000)
                    logger.info("WhatsApp session is valid (alternative selector)")
                    return True
                except PlaywrightTimeoutError:
                    # If we see QR code, we're not logged in
                    logger.warning("WhatsApp session expired - QR code scan required")
                    return False

        except Exception as e:
            logger.error(f"Error checking WhatsApp login status: {e}")
            return False

    async def send_message(self, contact: str, message: str) -> tuple[bool, str, str]:
        """
        Send message to WhatsApp contact.

        Args:
            contact: Contact name or phone number
            message: Message text to send

        Returns:
            (success, message_id, error_message) tuple
        """
        try:
            # Navigate to WhatsApp Web
            await self.page.goto('https://web.whatsapp.com', timeout=30000)

            # Check if logged in
            if not await self.is_logged_in():
                return False, "", "Not logged into WhatsApp Web. Please log in manually."

            # Search for contact
            try:
                search_box = await self.page.wait_for_selector(
                    'div[contenteditable="true"][data-tab="3"]',
                    timeout=10000
                )
                await search_box.click()
                await search_box.fill(contact)
                await asyncio.sleep(2)  # Wait for search results

                logger.info(f"Searched for contact: {contact}")
            except Exception as e:
                logger.error(f"Could not find search box: {e}")
                return False, "", "Could not find search box"

            # Click on the contact
            try:
                contact_element = await self.page.wait_for_selector(
                    f'span[title="{contact}"]',
                    timeout=10000
                )
                await contact_element.click()
                await asyncio.sleep(1)  # Wait for chat to open

                logger.info(f"Opened chat with: {contact}")
            except Exception as e:
                logger.error(f"Could not find contact: {e}")
                return False, "", f"Could not find contact: {contact}"

            # Type message
            try:
                message_box = await self.page.wait_for_selector(
                    'div[contenteditable="true"][data-tab="10"]',
                    timeout=10000
                )
                await message_box.click()
                await message_box.fill(message)
                logger.info("Typed message")
            except Exception as e:
                logger.error(f"Could not find message box: {e}")
                return False, "", "Could not find message box"

            # Send message using Enter key (more reliable than button click)
            try:
                await self.page.keyboard.press('Enter')
                logger.info("Pressed Enter to send message")
            except Exception as e:
                logger.error(f"Could not send message: {e}")
                return False, "", "Could not send message"

            # Wait for message to be sent
            await asyncio.sleep(2)

            # Generate message ID
            message_id = f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Message sent successfully: {message_id}")

            return True, message_id, ""

        except Exception as e:
            error_msg = f"Error sending WhatsApp message: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool()
async def send_whatsapp_message(
    contact: str,
    message: str,
    entry_id: str = ""
) -> dict:
    """
    Send a WhatsApp message via browser automation.

    Args:
        contact: Contact name or phone number
        message: Message text to send (max 5000 characters)
        entry_id: Audit log entry ID for tracking (optional)

    Returns:
        {
            'success': True/False,
            'message_id': 'Unique message ID',
            'timestamp': 'ISO 8601 timestamp',
            'error': 'Error message if failed (None if successful)'
        }

    Raises:
        ValueError: If contact or message is invalid
    """
    start_time = datetime.utcnow()

    try:
        # Validate request with Pydantic
        request = WhatsAppMessageRequest(
            contact=contact,
            message=message
        )

        # Send message using browser automation
        async with WhatsAppBrowser() as browser:
            success, message_id, error = await browser.send_message(
                contact=request.contact,
                message=request.message
            )

            # Calculate execution time
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log to audit logger
            if entry_id:
                audit_logger.log_action_executed(
                    entry_id=entry_id,
                    action_type='send_whatsapp_message',
                    mcp_server='browser_mcp',
                    execution_time_ms=execution_time_ms,
                    success=success,
                    result={
                        'message_id': message_id,
                        'contact': contact,
                        'message_length': len(request.message)
                    },
                    error=error if not success else None
                )

            return {
                'success': success,
                'message_id': message_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': error if not success else None
            }

    except ValueError as e:
        # Validation error
        execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        error_msg = f"Validation error: {str(e)}"

        if entry_id:
            audit_logger.log_action_executed(
                entry_id=entry_id,
                action_type='send_whatsapp_message',
                mcp_server='browser_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'message_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': error_msg
        }
    except Exception as e:
        # Unexpected error
        execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        error_msg = f"Error: {str(e)}"

        if entry_id:
            audit_logger.log_action_executed(
                entry_id=entry_id,
                action_type='send_whatsapp_message',
                mcp_server='browser_mcp',
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg
            )

        return {
            'success': False,
            'message_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': error_msg
        }


@mcp.tool()
async def health_check() -> dict:
    """
    Check if WhatsApp Web session is valid and browser automation is working.

    Returns:
        {
            'status': 'healthy' or 'unhealthy',
            'logged_in': True/False,
            'message': 'Status message',
            'timestamp': 'ISO 8601 timestamp'
        }
    """
    try:
        # Check WhatsApp session
        try:
            async with WhatsAppBrowser() as browser:
                logged_in = await browser.is_logged_in()

                if logged_in:
                    return {
                        'status': 'healthy',
                        'logged_in': True,
                        'message': 'WhatsApp Web session is active',
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }
                else:
                    return {
                        'status': 'unhealthy',
                        'logged_in': False,
                        'message': 'WhatsApp Web session expired. Please scan QR code.',
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'logged_in': False,
                'message': f'Browser automation error: {str(e)}',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'logged_in': False,
            'message': f'Error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Browser MCP Server (WhatsApp)")
    logger.info(f"Vault root: {vault_root}")
    logger.info(f"Session directory: {SESSION_DIR}")
    logger.info(f"CDP port: {CDP_PORT}")
    mcp.run()
