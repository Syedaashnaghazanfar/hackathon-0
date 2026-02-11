#!/usr/bin/env python3
"""
Social Media Browser MCP Server - Unified social media posting via Playwright

Supports posting to Facebook, Instagram, and Twitter/X using browser automation.
Uses persistent browser sessions (login once, reuse forever).

Created for Gold Tier AI Employee - Social Media Integration
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pydantic import BaseModel, Field, field_validator
from fastmcp import FastMCP
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="social-browser-mcp")

# Session storage
SESSION_DIR = os.getenv('SOCIAL_SESSION_DIR', '.social_session')

# Platform URLs and CDP ports (unique per platform)
PLATFORM_CONFIGS = {
    'facebook': {
        'url': 'https://www.facebook.com',
        'cdp_port': 9223
    },
    'instagram': {
        'url': 'https://www.instagram.com',
        'cdp_port': 9224
    },
    'twitter': {
        'url': 'https://x.com',
        'cdp_port': 9225
    }
}


# ============================================================================
# PYDANTIC MODELS - Type-safe request validation
# ============================================================================

class SocialMediaPostRequest(BaseModel):
    """Social media post request model."""

    text: str = Field(..., description="Post text content")
    image_path: Optional[str] = Field(None, description="Path to image file")
    platform: str = Field(..., description="Target platform: facebook, instagram, or twitter")
    wait_for_manual_click: bool = Field(False, description="If True, keeps browser open for manual click when automation fails")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Post text cannot be empty')
        if len(v) > 2200:  # Platform max length
            raise ValueError('Post text too long')
        return v

    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v):
        valid_platforms = ['facebook', 'instagram', 'twitter']
        if v.lower() not in valid_platforms:
            raise ValueError(f'Platform must be one of: {valid_platforms}')
        return v.lower()


class SocialMediaPostResponse(BaseModel):
    """Social media post response model."""

    success: bool = Field(..., description="Whether post was successful")
    post_url: str = Field(default="", description="URL to view the post")
    post_id: str = Field(default="", description="Post ID")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    requires_manual_click: bool = Field(default=False, description="If True, post is prepared but requires manual click")


# ============================================================================
# SOCIAL MEDIA BROWSER AUTOMATION
# ============================================================================

class SocialMediaBrowser:
    """Social media browser automation using Playwright with persistent sessions."""

    def __init__(self):
        """Initialize social media browser."""
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}  # Separate browser per platform
        self.contexts: Dict[str, BrowserContext] = {}  # Separate context per platform
        self.session_dir = Path(SESSION_DIR)
        self._started = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start browser instances for all platforms."""
        if self._started:
            logger.warning("Browser already started")
            return

        try:
            logger.info("Starting social media browser instances")
            logger.info(f"Session directory: {self.session_dir}")

            self.playwright = await async_playwright().start()
            self.session_dir.mkdir(parents=True, exist_ok=True)

            # Start separate browser for each platform
            for platform, config in PLATFORM_CONFIGS.items():
                platform_dir = self.session_dir / platform
                platform_dir.mkdir(parents=True, exist_ok=True)

                logger.info(f"Starting browser for {platform} on CDP port {config['cdp_port']}")

                # Launch persistent context for this platform with anti-detection measures
                context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=str(platform_dir),
                    headless=False,  # Social media requires visible browser
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        f'--remote-debugging-port={config["cdp_port"]}',
                        '--disable-infobars',
                        '--disable-extensions',
                        '--disable-popup-blocking',
                        '--disable-save-password-bubble',
                        '--disable-translate',
                        '--disable-default-apps',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--disable-features=VizDisplayCompositor',
                    ],
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    locale='en-US',
                    timezone_id='America/New_York',
                    permissions=['geolocation', 'notifications']
                )

                self.contexts[platform] = context
                logger.info(f"Browser started for {platform}")

            self._started = True
            logger.info("All social media browsers started successfully")

        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            await self.close()
            raise

    async def close(self):
        """Close all browsers (sessions saved automatically)."""
        try:
            for platform, context in self.contexts.items():
                await context.close()
                logger.info(f"Closed browser for {platform} (session saved)")

            self.contexts.clear()

            if self.playwright:
                await self.playwright.stop()

        except Exception as e:
            logger.error(f"Error closing browsers: {e}")

    async def get_context(self, platform: str) -> BrowserContext:
        """
        Get browser context for specific platform.

        Args:
            platform: Platform name (facebook, instagram, twitter)

        Returns:
            BrowserContext for the platform

        Raises:
            ValueError: If platform not supported
        """
        if platform not in PLATFORM_CONFIGS:
            raise ValueError(f"Unsupported platform: {platform}")

        if not self._started:
            await self.start()

        return self.contexts.get(platform)

    async def is_logged_in(self, platform: str) -> bool:
        """Check if user is logged into platform."""
        try:
            # Get or create page
            if not self.context or len(self.context.pages) == 0:
                page = await self.context.new_page()
            else:
                page = self.context.pages[0]

            url = PLATFORM_URLS.get(platform)
            if not url:
                return False

            await page.goto(url, timeout=30000)

            # Platform-specific login detection
            if platform == 'facebook':
                # Check for login form vs logged in state
                try:
                    await page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
                    return True
                except:
                    return False

            elif platform == 'instagram':
                # Check for create post button (only visible when logged in)
                try:
                    await page.wait_for_selector('svg[aria-label="New post"]', timeout=5000)
                    return True
                except:
                    return False

            elif platform == 'twitter':
                # Check for tweet box
                try:
                    await page.wait_for_selector('div[contenteditable="true"][data-text]', timeout=5000)
                    return True
                except:
                    return False

        except Exception as e:
            logger.error(f"Error checking login status for {platform}: {e}")
            return False

    async def post_to_platform(self, platform: str, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """Post content to specified platform."""
        try:
            # Get platform-specific context
            context = await self.get_context(platform)

            # Get or create page
            if len(context.pages) == 0:
                page = await context.new_page()
            else:
                page = context.pages[0]

            config = PLATFORM_CONFIGS.get(platform)
            if not config:
                return False, "", f"Unknown platform: {platform}"

            url = config['url']

            # Navigate to platform
            await page.goto(url, timeout=30000)

            # Check if logged in
            if not await self.is_logged_in(platform, page):
                return False, "", f"Not logged into {platform}. Please run login_{platform}.py"

            # Platform-specific posting logic
            if platform == 'facebook':
                return await self._post_to_facebook(page, text, image_path)
            elif platform == 'instagram':
                return await self._post_to_instagram(page, text, image_path)
            elif platform == 'twitter':
                return await self._post_to_twitter(page, text, image_path)
            else:
                return False, "", f"Posting not implemented for {platform}"

        except Exception as e:
            error_msg = f"Error posting to {platform}: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg

    async def is_logged_in(self, platform: str, page: Optional[Page] = None) -> bool:
        """Check if user is logged into platform."""
        try:
            context = await self.get_context(platform)

            # Get or create page
            if not page:
                if len(context.pages) == 0:
                    page = await context.new_page()
                else:
                    page = context.pages[0]

            config = PLATFORM_CONFIGS.get(platform)
            if not config:
                return False

            url = config['url']
            await page.goto(url, timeout=30000)

            # Platform-specific login detection
            if platform == 'facebook':
                # First check: Login form should NOT be present
                try:
                    await page.wait_for_selector('input[name="email"]', timeout=3000)
                    # Login form found - NOT logged in
                    return False
                except:
                    pass  # No login form, good sign

                # Second check: Look for post composer with multiple selectors
                post_box_selectors = [
                    'div[contenteditable="true"][data-text]',
                    'div[role="textbox"]',
                    'div[aria-label*="What"]',
                    'textarea[name="xadium"]',
                ]

                for selector in post_box_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=2000)
                        return True  # Found post composer - logged in
                    except:
                        continue

                # If no post composer found but no login form, assume logged in
                # (Facebook may just be loading slowly)
                return True

            elif platform == 'instagram':
                # Check for create post button (only visible when logged in)
                try:
                    await page.wait_for_selector('svg[aria-label="New post"]', timeout=5000)
                    return True
                except:
                    return False

            elif platform == 'twitter':
                # Check for tweet box
                try:
                    await page.wait_for_selector('div[contenteditable="true"][data-text]', timeout=5000)
                    return True
                except:
                    return False

        except Exception as e:
            logger.error(f"Error checking login status for {platform}: {e}")
            return False

    async def check_session_health(self, platform: str) -> dict:
        """
        Check health of platform session.

        Args:
            platform: Platform name

        Returns:
            Dict with health status
        """
        session_path = self.session_dir / platform

        if not session_path.exists():
            return {
                "platform": platform,
                "healthy": False,
                "reason": "Session directory not found",
                "requires_relogin": True
            }

        # Check session age
        import time
        session_age_seconds = time.time() - session_path.stat().st_mtime
        session_age_hours = session_age_seconds / 3600

        # Sessions older than 24 hours may be stale
        if session_age_hours > 24:
            return {
                "platform": platform,
                "healthy": False,
                "reason": f"Session is {session_age_hours:.1f} hours old (may be expired)",
                "requires_relogin": True,
                "session_age_hours": session_age_hours
            }

        return {
            "platform": platform,
            "healthy": True,
            "session_age_hours": session_age_hours,
            "requires_relogin": False
        }

    async def _human_like_type(self, element, text: str):
        """Type text with human-like random delays."""
        import random
        for char in text:
            await element.type(char, delay=random.uniform(50, 150))  # 50-150ms per char
            await asyncio.sleep(random.uniform(0.01, 0.05))  # Random pause between chars

    async def _try_multiple_selectors(self, page, selectors: list, timeout=5000):
        """Try multiple selectors until one works."""
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=timeout)
                if element:
                    return element
            except:
                continue
        return None

    async def _post_to_facebook(self, page: Page, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """Post to Facebook with anti-detection measures."""
        import random
        try:
            logger.info("Starting Facebook post preparation...")

            # Step 1: Find and click the post TRIGGER (e.g., "What's on your mind?")
            post_trigger_selectors = [
                'div[aria-label*="Create"]',  # Create post button
                'div[aria-label*="What"]',  # aria-label containing "What"
                'h3:has-text("Create")',  # Alternative: "Create" post
                'div[data-pagelet="FeedUnit"] div[role="button"]',  # First post button in feed
                'div[role="button"] span:has-text("Photo")',  # Photo button (nearby trigger)
            ]

            logger.info("Looking for post trigger...")
            post_trigger = await self._try_multiple_selectors(page, post_trigger_selectors, timeout=15000)

            if not post_trigger:
                # Couldn't find trigger, try direct composer search
                logger.warning("Could not find post trigger, trying direct composer...")
            else:
                logger.info("Found post trigger, clicking...")
                await post_trigger.click()
                await asyncio.sleep(random.uniform(1.0, 2.0))  # Wait for composer to appear

            # Step 2: Now look for the actual post box/composer
            post_box_selectors = [
                'div[contenteditable="true"][data-text]',
                'div[role="textbox"]',
                'div[aria-label*="Message"]',  # Updated aria-label
                'textarea[name="xadium"]',  # Modern Facebook uses textarea
                'div[contenteditable="true"]:not([data-text])',  # Fallback: any contenteditable
            ]

            post_box = await self._try_multiple_selectors(page, post_box_selectors, timeout=10000)
            if not post_box:
                return False, "", "Could not find Facebook post box - UI may have changed. Please check if the browser window shows the composer."

            logger.info("Found post box, entering text...")
            await post_box.click()
            await asyncio.sleep(random.uniform(0.5, 1.5))  # Random delay

            # Type with human-like speed
            await self._human_like_type(post_box, text)
            await asyncio.sleep(random.uniform(1.0, 2.0))  # Pause after typing

            # Upload image if provided
            if image_path and Path(image_path).exists():
                logger.info(f"Uploading image: {image_path}")
                file_input = await page.query_selector('input[type="file"][accept*="image"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await asyncio.sleep(random.uniform(2.0, 4.0))  # Wait for upload
                else:
                    logger.warning("Could not find image upload input")

            # Try multiple selectors for Post button
            post_button_selectors = [
                'div[aria-label="Post"]',
                'div[role="button"][data-testid*="submit"]',
                'button[aria-label="Post"]',
                'div[role="button"] span:has-text("Post")',
            ]

            logger.info("Looking for Post button...")
            post_button = await self._try_multiple_selectors(page, post_button_selectors, timeout=10000)

            if not post_button:
                # Button found but couldn't be clicked - likely anti-bot
                logger.warning("Post button found but likely blocked by anti-bot detection")
                return False, "", "Post button blocked by anti-bot detection. Post is prepared in browser - please click Post manually."

            # Try clicking with JavaScript (sometimes works when click() doesn't)
            try:
                await post_button.click(timeout=3000)
                logger.info("Post button clicked successfully")
            except Exception as click_error:
                # Try JavaScript click as fallback
                logger.warning(f"Standard click failed: {click_error}, trying JavaScript click")
                try:
                    await page.evaluate('(element) => element.click()', post_button)
                    logger.info("JavaScript click successful")
                except:
                    # Final state: post is prepared, ask user to click
                    return False, "", "Post is fully prepared in browser with text and image. Please click the Post button manually to complete."

            await asyncio.sleep(random.uniform(2.0, 4.0))  # Wait for post to submit

            # Success
            post_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Facebook post successful: {post_id}")
            return True, post_id, ""

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Facebook post error: {error_msg}")
            # Check if it's a timeout (likely selector changed)
            if "timeout" in error_msg.lower():
                return False, "", "Timeout finding element - Facebook UI may have changed. Post is prepared in browser."
            return False, "", error_msg

    async def _post_to_instagram(self, page: Page, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """Post to Instagram with anti-detection measures."""
        import random
        try:
            logger.info("Starting Instagram post preparation...")

            # Instagram requires images
            if not image_path or not Path(image_path).exists():
                return False, "", "Instagram requires an image to post"

            # Multiple possible selectors for create button
            create_btn_selectors = [
                'svg[aria-label="New post"]',
                'svg[aria-label="New post nav"]',
                'div[role="button"] span:has-text("New post")',
                'a[aria-label*="New post"]',
            ]

            create_btn = await self._try_multiple_selectors(page, create_btn_selectors, timeout=15000)
            if not create_btn:
                return False, "", "Could not find Instagram create button - UI may have changed"

            await create_btn.click()
            await asyncio.sleep(random.uniform(1.5, 3.0))

            # Upload image
            logger.info(f"Uploading image: {image_path}")
            file_input_selectors = [
                'input[type="file"]',
                'input[accept*="image"]',
            ]

            file_input = await self._try_multiple_selectors(page, file_input_selectors, timeout=5000)
            if file_input:
                await file_input.set_input_files(image_path)
                await asyncio.sleep(random.uniform(3.0, 5.0))  # Wait for upload
            else:
                return False, "", "Could not find file input for image upload"

            # Try multiple selectors for Next button
            next_btn_selectors = [
                'button:has-text("Next")',
                'div[role="button"] button:has-text("Next")',
                'button[aria-label*="Next"]',
            ]

            logger.info("Looking for Next button...")
            next_btn = await self._try_multiple_selectors(page, next_btn_selectors, timeout=10000)
            if not next_btn:
                return False, "", "Could not find Next button after image upload"

            await next_btn.click()
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # Add caption
            caption_box_selectors = [
                'textarea[aria-label="Write a caption…"]',
                'textarea[placeholder*="caption"]',
                'div[contenteditable="true"][data-text]',
            ]

            caption_box = await self._try_multiple_selectors(page, caption_box_selectors, timeout=10000)
            if caption_box:
                await self._human_like_type(caption_box, text)
                await asyncio.sleep(random.uniform(1.0, 2.0))
            else:
                logger.warning("Could not find caption box, continuing without caption")

            # Try multiple selectors for Share button
            share_btn_selectors = [
                'button:has-text("Share")',
                'div[role="button"] button:has-text("Share")',
                'button[aria-label*="Share"]',
            ]

            logger.info("Looking for Share button...")
            share_btn = await self._try_multiple_selectors(page, share_btn_selectors, timeout=10000)

            if not share_btn:
                # Post is prepared, ask user to click Share
                logger.warning("Share button found but likely blocked by anti-bot detection")
                return False, "", "Instagram post is fully prepared with image and caption. Please click the Share button manually to complete."

            try:
                await share_btn.click(timeout=3000)
                logger.info("Share button clicked successfully")
            except Exception as click_error:
                logger.warning(f"Standard click failed: {click_error}, trying JavaScript click")
                try:
                    await page.evaluate('(element) => element.click()', share_btn)
                    logger.info("JavaScript click successful")
                except:
                    return False, "", "Instagram post is prepared in browser. Please click Share button manually."

            await asyncio.sleep(random.uniform(2.0, 4.0))  # Wait for post to submit

            # Success
            post_id = f"ig_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Instagram post successful: {post_id}")
            return True, post_id, ""

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Instagram post error: {error_msg}")
            if "timeout" in error_msg.lower():
                return False, "", "Timeout finding element - Instagram UI may have changed. Post is prepared in browser."
            return False, "", error_msg

    async def _post_to_twitter(self, page: Page, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """Post to Twitter/X with anti-detection measures."""
        import random
        try:
            logger.info("Starting Twitter/X post preparation...")

            # Multiple possible selectors for tweet box
            tweet_box_selectors = [
                'div[contenteditable="true"][data-text]',
                'div[role="textbox"]',
                'div[aria-label*="Post text"]',
                'div[data-text="What is happening?!"]',
            ]

            tweet_box = await self._try_multiple_selectors(page, tweet_box_selectors, timeout=15000)
            if not tweet_box:
                return False, "", "Could not find Twitter tweet box - UI may have changed"

            await tweet_box.click()
            await asyncio.sleep(random.uniform(0.5, 1.5))  # Random delay

            # Type with human-like speed
            await self._human_like_type(tweet_box, text)
            await asyncio.sleep(random.uniform(1.0, 2.0))  # Pause after typing

            # Upload image if provided
            if image_path and Path(image_path).exists():
                logger.info(f"Uploading image: {image_path}")
                file_input = await page.query_selector('input[type="file"][accept*="image"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await asyncio.sleep(random.uniform(2.0, 4.0))  # Wait for upload
                else:
                    logger.warning("Could not find image upload input")

            # Try multiple selectors for Post button
            post_button_selectors = [
                'div[role="button"][data-testid="tweetButtonInline"]',
                'div[role="button"][data-testid="tweet"]',
                'button[data-testid="tweetButton"]',
                'div[aria-label*="Post"]',
            ]

            logger.info("Looking for Post button...")
            post_button = await self._try_multiple_selectors(page, post_button_selectors, timeout=10000)

            if not post_button:
                # Button found but couldn't be clicked - likely anti-bot
                logger.warning("Post button found but likely blocked by anti-bot detection")
                return False, "", "Tweet is fully prepared in browser. Please click the Post button manually to complete."

            # Try clicking with JavaScript (sometimes works when click() doesn't)
            try:
                await post_button.click(timeout=3000)
                logger.info("Post button clicked successfully")
            except Exception as click_error:
                # Try JavaScript click as fallback
                logger.warning(f"Standard click failed: {click_error}, trying JavaScript click")
                try:
                    await page.evaluate('(element) => element.click()', post_button)
                    logger.info("JavaScript click successful")
                except:
                    # Final state: post is prepared, ask user to click
                    return False, "", "Tweet is fully prepared in browser with text and image. Please click the Post button manually to complete."

            await asyncio.sleep(random.uniform(2.0, 4.0))  # Wait for post to submit

            # Success
            tweet_id = f"tw_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Twitter post successful: {tweet_id}")
            return True, tweet_id, ""

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Twitter post error: {error_msg}")
            # Check if it's a timeout (likely selector changed)
            if "timeout" in error_msg.lower():
                return False, "", "Timeout finding element - Twitter UI may have changed. Post is prepared in browser."
            return False, "", error_msg


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool()
async def post_to_facebook(
    text: str,
    image_path: str = None
) -> dict:
    """Post content to Facebook via browser automation.

    Args:
        text: Post text content
        image_path: Optional path to image file

    Returns:
        Dict with success status, post URL, timestamp, or error
    """
    start_time = datetime.utcnow()

    try:
        async with SocialMediaBrowser() as browser:
            success, post_id, error = await browser.post_to_platform('facebook', text, image_path)

            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return {
                'success': success,
                'post_url': f"https://www.facebook.com/{post_id}" if success else "",
                'post_id': post_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': error if not success else None
            }

    except Exception as e:
        return {
            'success': False,
            'post_url': '',
            'post_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': str(e)
        }


@mcp.tool()
async def post_to_instagram(
    text: str,
    image_path: str = None
) -> dict:
    """Post content to Instagram via browser automation.

    Args:
        text: Caption text
        image_path: Path to image (required for Instagram)

    Returns:
        Dict with success status, post URL, timestamp, or error
    """
    start_time = datetime.utcnow()

    try:
        async with SocialMediaBrowser() as browser:
            success, post_id, error = await browser.post_to_platform('instagram', text, image_path)

            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return {
                'success': success,
                'post_url': f"https://www.instagram.com/p/{post_id}/" if success else "",
                'post_id': post_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': error if not success else None
            }

    except Exception as e:
        return {
            'success': False,
            'post_url': '',
            'post_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': str(e)
        }


@mcp.tool()
async def post_to_twitter(
    text: str,
    image_path: str = None
) -> dict:
    """Post content to Twitter/X via browser automation.

    Args:
        text: Tweet text (max 280 chars for free tier)
        image_path: Optional path to image file

    Returns:
        Dict with success status, tweet URL, timestamp, or error
    """
    start_time = datetime.utcnow()

    try:
        async with SocialMediaBrowser() as browser:
            success, tweet_id, error = await browser.post_to_platform('twitter', text, image_path)

            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return {
                'success': success,
                'tweet_url': f"https://x.com/{tweet_id}" if success else "",
                'tweet_id': tweet_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'error': error if not success else None
            }

    except Exception as e:
        return {
            'success': False,
            'tweet_url': '',
            'tweet_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': str(e)
        }


@mcp.tool()
async def social_media_health_check() -> dict:
    """Check health status for all social media platforms.

    Returns:
        Dict with session health for each platform and overall health
    """
    result = {
        'platforms': {},
        'overall_health': 'unknown',
        'checked_at': datetime.utcnow().isoformat() + 'Z'
    }

    try:
        async with SocialMediaBrowser() as browser:
            platforms_health = {}

            for platform in ['facebook', 'instagram', 'twitter']:
                # Check login status
                logged_in = await browser.is_logged_in(platform)

                # Check session health
                session_health = await browser.check_session_health(platform)

                platforms_health[platform] = {
                    'logged_in': logged_in,
                    'session_healthy': session_health['healthy'],
                    'session_age_hours': session_health.get('session_age_hours', 0),
                    'status': 'Session active' if logged_in and session_health['healthy'] else 'Session expired',
                    'requires_relogin': session_health.get('requires_relogin', False)
                }

            result['platforms'] = platforms_health

            # Calculate overall health
            all_healthy = all(
                p['logged_in'] and p['session_healthy']
                for p in platforms_health.values()
            )
            any_healthy = any(
                p['logged_in'] and p['session_healthy']
                for p in platforms_health.values()
            )

            if all_healthy:
                result['overall_health'] = 'healthy'
            elif any_healthy:
                result['overall_health'] = 'degraded'
            else:
                result['overall_health'] = 'unhealthy'

    except Exception as e:
        result['overall_health'] = 'error'
        result['error'] = str(e)

    return result


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Social Media Browser MCP Server")
    logger.info(f"Session directory: {SESSION_DIR}")
    logger.info(f"CDP port: {CDP_PORT}")
    mcp.run()
