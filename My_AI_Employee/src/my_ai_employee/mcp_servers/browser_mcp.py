"""
Browser automation MCP server for Silver Tier AI Employee.

Implements FastMCP server with send_whatsapp_message tool using Playwright.
"""

import os
import logging
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from my_ai_employee.config import get_config


logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("browser")


@mcp.tool()
def send_whatsapp_message(
    contact: str,
    message: str,
) -> dict:
    """
    Send WhatsApp message via browser automation.

    Args:
        contact: Contact name or phone number
        message: Message text to send

    Returns:
        Dictionary with status and details

    Example:
        >>> send_whatsapp_message(
        ...     contact="John Doe",
        ...     message="Hello, this is a test message."
        ... )
        {'status': 'success', 'contact': 'John Doe', 'message_preview': 'Hello, this...'}
    """
    config = get_config()

    # Check dry-run mode
    if config.dry_run:
        logger.info(f"DRY RUN: Would send WhatsApp message to {contact}")
        logger.info(f"DRY RUN: Message preview: {message[:100]}...")
        return {
            "status": "dry_run",
            "message": f"Dry-run mode: WhatsApp message to {contact} not actually sent",
            "contact": contact,
            "message_preview": message[:100],
        }

    try:
        session_dir = Path(config.whatsapp_session_dir)

        with sync_playwright() as p:
            # Launch browser with persistent session
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,  # WhatsApp Web requires non-headless for QR scan
                args=["--disable-blink-features=AutomationControlled"],
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://web.whatsapp.com")

            # Check if logged in (wait for chat list)
            try:
                page.wait_for_selector("div[data-testid='chat']", timeout=30000)
                logger.info("WhatsApp Web: Already logged in")
            except PlaywrightTimeoutError:
                # Not logged in, need QR scan
                logger.warning(
                    "WhatsApp Web: Not logged in. QR code scan required. "
                    "Please scan QR code with mobile app..."
                )
                try:
                    page.wait_for_selector("div[data-testid='chat']", timeout=120000)
                    logger.info("WhatsApp Web: QR code scanned successfully")
                except PlaywrightTimeoutError:
                    browser.close()
                    return {
                        "status": "error",
                        "error_type": "authentication_timeout",
                        "error_message": "QR code not scanned within 2 minutes. Please re-authenticate.",
                    }

            # Search for contact
            search_box = page.locator("div[contenteditable='true'][data-tab='3']")
            search_box.click()
            search_box.fill(contact)
            page.wait_for_timeout(1000)  # Wait for search results

            # Click on first matching contact
            try:
                contact_elem = page.locator(f"span[title='{contact}']").first
                contact_elem.click(timeout=5000)
            except PlaywrightTimeoutError:
                browser.close()
                return {
                    "status": "error",
                    "error_type": "contact_not_found",
                    "error_message": f"Contact '{contact}' not found in WhatsApp",
                    "contact": contact,
                }

            # Wait for chat to load
            page.wait_for_selector("div[data-testid='conversation-compose-box-input']", timeout=10000)

            # Type message
            message_box = page.locator("div[data-testid='conversation-compose-box-input']")
            message_box.click()
            message_box.fill(message)
            page.wait_for_timeout(500)

            # Send message (press Enter)
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)  # Wait for message to send

            logger.info(f"WhatsApp message sent to {contact}")

            browser.close()

            return {
                "status": "success",
                "contact": contact,
                "message_preview": message[:100],
            }

    except PlaywrightTimeoutError as e:
        logger.error(f"WhatsApp automation timeout: {e}")
        return {
            "status": "error",
            "error_type": "timeout",
            "error_message": "WhatsApp Web automation timed out. Please check browser.",
            "contact": contact,
        }

    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": "unknown_error",
            "error_message": str(e),
            "contact": contact,
        }


@mcp.tool()
def check_whatsapp_auth() -> dict:
    """
    Check if WhatsApp Web is authenticated.

    Returns:
        Dictionary with authentication status

    Example:
        >>> check_whatsapp_auth()
        {'status': 'authenticated', 'session_valid': True}
    """
    config = get_config()

    try:
        session_dir = Path(config.whatsapp_session_dir)

        if not session_dir.exists():
            return {
                "status": "not_authenticated",
                "session_valid": False,
                "message": "WhatsApp session directory does not exist. Run whatsapp_auth.py first.",
            }

        with sync_playwright() as p:
            # Launch browser with persistent session
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://web.whatsapp.com")

            # Check if logged in
            try:
                page.wait_for_selector("div[data-testid='chat']", timeout=10000)
                browser.close()
                return {
                    "status": "authenticated",
                    "session_valid": True,
                }
            except PlaywrightTimeoutError:
                browser.close()
                return {
                    "status": "not_authenticated",
                    "session_valid": False,
                    "message": "WhatsApp session expired. Re-authenticate with QR code.",
                }

    except Exception as e:
        logger.error(f"Failed to check WhatsApp auth: {e}", exc_info=True)
        return {
            "status": "error",
            "session_valid": False,
            "error": str(e),
        }


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
