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
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
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

                # Launch persistent context for this platform
                context = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=str(platform_dir),
                    headless=False,  # Social media requires visible browser
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        f'--remote-debugging-port={config["cdp_port"]}'
                    ],
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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

    async def _post_to_facebook(self, page: Page, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """Post to Facebook."""
        try:
            # Click post box
            post_box = await page.wait_for_selector('div[contenteditable="true"]', timeout=10000)
            await post_box.click()
            await asyncio.sleep(1)

            # Type text
            await post_box.fill(text)

            # Upload image if provided
            if image_path and Path(image_path).exists():
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await asyncio.sleep(2)

            # Click post button
            post_button = await page.wait_for_selector('div[role="button"] > span:has-text("Post")', timeout=5000)
            await post_button.click()
            await asyncio.sleep(3)

            # Success
            post_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return True, post_id, ""

        except Exception as e:
            return False, "", str(e)

    async def _post_to_instagram(self, page: Page, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """Post to Instagram."""
        try:
            # Instagram requires images
            if not image_path or not Path(image_path).exists():
                return False, "", "Instagram requires an image"

            # Click create post button
            create_btn = await page.wait_for_selector('svg[aria-label="New post"]', timeout=10000)
            await create_btn.click()
            await asyncio.sleep(2)

            # Upload image
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(image_path)
                await asyncio.sleep(3)

            # Click next
            next_btn = await page.wait_for_selector('div[role="button"] > button:has-text("Next")', timeout=5000)
            await next_btn.click()
            await asyncio.sleep(1)

            # Add caption
            caption_box = await page.wait_for_selector('textarea[aria-label="Write a caption…"]', timeout=5000)
            await caption_box.fill(text)

            # Share
            share_btn = await page.wait_for_selector('div[role="button"] > button:has-text("Share")', timeout=5000)
            await share_btn.click()
            await asyncio.sleep(3)

            # Success
            post_id = f"ig_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return True, post_id, ""

        except Exception as e:
            return False, "", str(e)

    async def _post_to_twitter(self, page: Page, text: str, image_path: Optional[str] = None) -> tuple[bool, str, str]:
        """Post to Twitter/X."""
        try:
            # Click tweet box
            tweet_box = await page.wait_for_selector('div[contenteditable="true"][data-text]', timeout=10000)
            await tweet_box.click()
            await asyncio.sleep(1)

            # Type text
            await tweet_box.fill(text)

            # Upload image if provided
            if image_path and Path(image_path).exists():
                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(image_path)
                    await asyncio.sleep(2)

            # Click post button
            post_button = await page.wait_for_selector('div[role="button"][data-testid="tweetButtonInline"]', timeout=5000)
            await post_button.click()
            await asyncio.sleep(3)

            # Success
            tweet_id = f"tw_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            return True, tweet_id, ""

        except Exception as e:
            return False, "", str(e)


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
