#!/usr/bin/env python3
"""
Facebook Login Helper - Authenticate and save browser session for social media automation

This script opens a browser to Facebook login page and waits for manual authentication.
Once authenticated, the session is saved to .social_session/facebook/ for reuse.

Usage:
    python login_facebook.py

Author: Gold Tier AI Employee
Date: 2026-02-05
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext
except ImportError:
    print("Playwright not installed. Run: uv add playwright && uv run playwright install chromium")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Session configuration
# Save sessions at project root (go up from scripts/skill-name/skills/.claude/)
SESSION_DIR = Path(__file__).parent.parent.parent.parent.parent / ".social_session"
PLATFORM = "facebook"
FACEBOOK_URL = "https://www.facebook.com"
CDP_PORT = 9223


async def login_facebook():
    """
    Open Facebook login page and wait for user to authenticate.

    Session is automatically saved to .social_session/facebook/ for reuse.
    """
    platform_dir = SESSION_DIR / PLATFORM
    platform_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting Facebook login helper")
    logger.info(f"Session directory: {platform_dir}")
    logger.info(f"CDP port: {CDP_PORT}")

    playwright = await async_playwright().start()

    try:
        # Launch browser with persistent context
        logger.info("Launching browser...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(platform_dir),
            headless=False,  # Show browser for manual login
            args=[
                '--disable-blink-features=AutomationControlled',
                f'--remote-debugging-port={CDP_PORT}'
            ],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        # Get or create page
        if len(context.pages) == 0:
            page = await context.new_page()
        else:
            page = context.pages[0]

        # Navigate to Facebook
        logger.info(f"Navigating to {FACEBOOK_URL}")
        await page.goto(FACEBOOK_URL, timeout=30000)

        # Wait for user to log in
        logger.info("")
        logger.info("=" * 70)
        logger.info("BROWSER OPENED - Please log in to Facebook")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Instructions:")
        logger.info("1. Log in to Facebook with your credentials")
        logger.info("2. Complete any 2FA if required")
        logger.info("3. Once logged in, press Ctrl+C to save session and exit")
        logger.info("")

        # Check if already logged in
        try:
            await page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
            logger.info("✓ Already logged in to Facebook!")
            logger.info("")
            logger.info("Session saved. You can now use Facebook posting tools.")
            logger.info("")
        except:
            # Not logged in, wait for user
            logger.info("Waiting for you to log in...")
            logger.info("(Press Ctrl+C when done)")

            try:
                # Wait indefinitely until user presses Ctrl+C
                await asyncio.Event().wait()
            except KeyboardInterrupt:
                logger.info("")

        # Verify login success
        try:
            await page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
            logger.info("✓ Successfully authenticated to Facebook!")
        except:
            logger.warning("⚠ Could not verify login. You may need to try again.")

        # Session is automatically saved by Playwright
        logger.info(f"Session saved to: {platform_dir}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("- Run: uv run python scripts/social_browser_mcp.py")
        logger.info("- Use MCP tool: post_to_facebook")

        # Close browser
        await context.close()
        await playwright.stop()

    except Exception as e:
        logger.error(f"Error during login: {e}")
        await playwright.stop()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(login_facebook())
    except KeyboardInterrupt:
        logger.info("\nLogin helper stopped by user")
        sys.exit(0)
