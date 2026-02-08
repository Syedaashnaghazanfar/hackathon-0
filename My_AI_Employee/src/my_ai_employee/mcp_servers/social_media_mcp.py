"""
Social Media MCP server for Gold Tier AI Employee.

Implements FastMCP server with tools for posting to Facebook, Instagram, and Twitter/X
using Playwright browser automation with persistent sessions.
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastmcp import FastMCP
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from my_ai_employee.config import get_config


logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("social-media")


# Platform configurations
PLATFORM_CONFIGS = {
    'facebook': {
        'url': 'https://www.facebook.com',
        'cdp_port': 9223,
        'session_dir': '.social_session/facebook',
    },
    'instagram': {
        'url': 'https://www.instagram.com',
        'cdp_port': 9224,
        'session_dir': '.social_session/instagram',
    },
    'twitter': {
        'url': 'https://x.com',
        'cdp_port': 9225,
        'session_dir': '.social_session/twitter',
    }
}


def _check_login_status(page, platform: str) -> bool:
    """Check if user is logged into platform."""
    try:
        if platform == 'facebook':
            # Check for post creation box
            page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
            return True
        elif platform == 'instagram':
            # Check for create post button
            page.wait_for_selector('svg[aria-label="New post"]', timeout=5000)
            return True
        elif platform == 'twitter':
            # Check for tweet box
            page.wait_for_selector('div[contenteditable="true"][data-text]', timeout=5000)
            return True
    except PlaywrightTimeoutError:
        return False

    return False


def _post_to_facebook(page, text: str, image_path: Optional[str] = None) -> dict:
    """Post to Facebook."""
    try:
        # Click post box
        post_box = page.wait_for_selector('div[contenteditable="true"]', timeout=10000)
        post_box.click()
        time.sleep(1)

        # Type text
        post_box.fill(text)

        # Upload image if provided
        if image_path and Path(image_path).exists():
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(image_path)
                time.sleep(2)

        # Click post button
        post_button = page.wait_for_selector('div[role="button"] > span:has-text("Post")', timeout=5000)
        post_button.click()
        time.sleep(3)

        post_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Successfully posted to Facebook: {post_id}")

        return {
            "success": True,
            "post_id": post_id,
            "post_url": f"https://www.facebook.com/{post_id}"
        }

    except Exception as e:
        logger.error(f"Failed to post to Facebook: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _post_to_instagram(page, text: str, image_path: Optional[str] = None) -> dict:
    """Post to Instagram."""
    try:
        # Instagram requires images
        if not image_path or not Path(image_path).exists():
            return {
                "success": False,
                "error": "Instagram requires an image"
            }

        # Click create post button
        create_btn = page.wait_for_selector('svg[aria-label="New post"]', timeout=10000)
        create_btn.click()
        time.sleep(2)

        # Upload image
        file_input = page.query_selector('input[type="file"]')
        if file_input:
            file_input.set_input_files(image_path)
            time.sleep(3)

        # Click next
        next_btn = page.wait_for_selector('div[role="button"] > button:has-text("Next")', timeout=5000)
        next_btn.click()
        time.sleep(1)

        # Add caption
        caption_box = page.wait_for_selector('textarea[aria-label="Write a caption…"]', timeout=5000)
        caption_box.fill(text)

        # Share
        share_btn = page.wait_for_selector('div[role="button"] > button:has-text("Share")', timeout=5000)
        share_btn.click()
        time.sleep(3)

        post_id = f"ig_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Successfully posted to Instagram: {post_id}")

        return {
            "success": True,
            "post_id": post_id,
            "post_url": f"https://www.instagram.com/p/{post_id}/"
        }

    except Exception as e:
        logger.error(f"Failed to post to Instagram: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _post_to_twitter(page, text: str, image_path: Optional[str] = None) -> dict:
    """Post to Twitter/X."""
    try:
        # Click tweet box
        tweet_box = page.wait_for_selector('div[contenteditable="true"][data-text]', timeout=10000)
        tweet_box.click()
        time.sleep(1)

        # Type text
        tweet_box.fill(text)

        # Upload image if provided
        if image_path and Path(image_path).exists():
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(image_path)
                time.sleep(2)

        # Click post button
        post_button = page.wait_for_selector('div[role="button"][data-testid="tweetButtonInline"]', timeout=5000)
        post_button.click()
        time.sleep(3)

        tweet_id = f"tw_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Successfully posted to Twitter: {tweet_id}")

        return {
            "success": True,
            "post_id": tweet_id,
            "post_url": f"https://x.com/{tweet_id}"
        }

    except Exception as e:
        logger.error(f"Failed to post to Twitter: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def post_to_facebook(
    text: str,
    image_path: Optional[str] = None
) -> dict:
    """
    Post content to Facebook via browser automation.

    Args:
        text: Post text content
        image_path: Optional path to image file

    Returns:
        Dictionary with success status, post URL, post ID, and timestamp

    Example:
        >>> post_to_facebook(
        ...     text="Hello, World!",
        ...     image_path="/path/to/image.jpg"
        ... )
        {'success': True, 'post_id': 'fb_20250208_123456', 'post_url': 'https://...'}
    """
    config = get_config()

    # Check dry-run mode
    if config.dry_run:
        logger.info(f"DRY RUN: Would post to Facebook: {text[:100]}...")
        return {
            "status": "dry_run",
            "message": f"Dry-run mode: Facebook post not actually sent",
            "text_preview": text[:100],
        }

    try:
        platform_config = PLATFORM_CONFIGS['facebook']
        session_dir = Path(platform_config['session_dir'])
        session_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            # Launch persistent browser
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    f'--remote-debugging-port={platform_config["cdp_port"]}'
                ],
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(platform_config['url'], timeout=30000)

            # Check if logged in
            if not _check_login_status(page, 'facebook'):
                browser.close()
                return {
                    "success": False,
                    "error": "Not logged into Facebook. Please run login_facebook.py first."
                }

            # Post to Facebook
            result = _post_to_facebook(page, text, image_path)
            browser.close()

            result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            return result

    except Exception as e:
        logger.error(f"Failed to post to Facebook: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }


@mcp.tool()
def post_to_instagram(
    text: str,
    image_path: Optional[str] = None
) -> dict:
    """
    Post content to Instagram via browser automation.

    Args:
        text: Caption text
        image_path: Path to image (required for Instagram)

    Returns:
        Dictionary with success status, post URL, post ID, and timestamp

    Example:
        >>> post_to_instagram(
        ...     text="Beautiful sunset! #nature",
        ...     image_path="/path/to/image.jpg"
        ... )
        {'success': True, 'post_id': 'ig_20250208_123456', 'post_url': 'https://...'}
    """
    config = get_config()

    # Check dry-run mode
    if config.dry_run:
        logger.info(f"DRY RUN: Would post to Instagram: {text[:100]}...")
        return {
            "status": "dry_run",
            "message": f"Dry-run mode: Instagram post not actually sent",
            "text_preview": text[:100],
        }

    try:
        platform_config = PLATFORM_CONFIGS['instagram']
        session_dir = Path(platform_config['session_dir'])
        session_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            # Launch persistent browser
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    f'--remote-debugging-port={platform_config["cdp_port"]}'
                ],
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(platform_config['url'], timeout=30000)

            # Check if logged in
            if not _check_login_status(page, 'instagram'):
                browser.close()
                return {
                    "success": False,
                    "error": "Not logged into Instagram. Please run login_instagram.py first."
                }

            # Post to Instagram
            result = _post_to_instagram(page, text, image_path)
            browser.close()

            result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            return result

    except Exception as e:
        logger.error(f"Failed to post to Instagram: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }


@mcp.tool()
def post_to_twitter(
    text: str,
    image_path: Optional[str] = None
) -> dict:
    """
    Post content to Twitter/X via browser automation.

    Args:
        text: Tweet text (max 280 chars for free tier)
        image_path: Optional path to image file

    Returns:
        Dictionary with success status, tweet URL, tweet ID, and timestamp

    Example:
        >>> post_to_twitter(
        ...     text="Hello, Twitter!",
        ...     image_path="/path/to/image.jpg"
        ... )
        {'success': True, 'post_id': 'tw_20250208_123456', 'post_url': 'https://...'}
    """
    config = get_config()

    # Check dry-run mode
    if config.dry_run:
        logger.info(f"DRY RUN: Would post to Twitter: {text[:100]}...")
        return {
            "status": "dry_run",
            "message": f"Dry-run mode: Twitter post not actually sent",
            "text_preview": text[:100],
        }

    try:
        platform_config = PLATFORM_CONFIGS['twitter']
        session_dir = Path(platform_config['session_dir'])
        session_dir.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            # Launch persistent browser
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    f'--remote-debugging-port={platform_config["cdp_port"]}'
                ],
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(platform_config['url'], timeout=30000)

            # Check if logged in
            if not _check_login_status(page, 'twitter'):
                browser.close()
                return {
                    "success": False,
                    "error": "Not logged into Twitter. Please run login_twitter.py first."
                }

            # Post to Twitter
            result = _post_to_twitter(page, text, image_path)
            browser.close()

            result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
            return result

    except Exception as e:
        logger.error(f"Failed to post to Twitter: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }


@mcp.tool()
def social_media_health_check() -> dict:
    """
    Check health status for all social media platforms.

    Returns:
        Dictionary with session health for each platform and overall health

    Example:
        >>> social_media_health_check()
        {'platforms': {'facebook': {'logged_in': True, ...}, ...}, 'overall_health': 'healthy'}
    """
    result = {
        'platforms': {},
        'overall_health': 'unknown',
        'checked_at': datetime.utcnow().isoformat() + 'Z'
    }

    try:
        for platform, config in PLATFORM_CONFIGS.items():
            session_dir = Path(config['session_dir'])

            # Check session exists
            if not session_dir.exists():
                result['platforms'][platform] = {
                    'logged_in': False,
                    'session_healthy': False,
                    'status': 'Session directory not found',
                    'requires_relogin': True
                }
                continue

            # Check session age
            session_age_seconds = time.time() - session_dir.stat().st_mtime
            session_age_hours = session_age_seconds / 3600

            # Sessions older than 24 hours may be stale
            if session_age_hours > 24:
                result['platforms'][platform] = {
                    'logged_in': False,
                    'session_healthy': False,
                    'session_age_hours': round(session_age_hours, 1),
                    'status': f'Session expired ({session_age_hours:.1f} hours old)',
                    'requires_relogin': True
                }
                continue

            # Try to check actual login status
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch_persistent_context(
                        user_data_dir=str(session_dir),
                        headless=True,
                        args=['--disable-blink-features=AutomationControlled']
                    )

                    page = browser.pages[0] if browser.pages else browser.new_page()
                    page.goto(config['url'], timeout=30000)

                    logged_in = _check_login_status(page, platform)
                    browser.close()

                    result['platforms'][platform] = {
                        'logged_in': logged_in,
                        'session_healthy': logged_in,
                        'session_age_hours': round(session_age_hours, 1),
                        'status': 'Session active' if logged_in else 'Session expired',
                        'requires_relogin': not logged_in
                    }

            except Exception as e:
                result['platforms'][platform] = {
                    'logged_in': False,
                    'session_healthy': False,
                    'status': f'Error checking: {str(e)}',
                    'requires_relogin': True
                }

        # Calculate overall health
        all_healthy = all(
            p['logged_in'] and p['session_healthy']
            for p in result['platforms'].values()
        )
        any_healthy = any(
            p['logged_in'] and p['session_healthy']
            for p in result['platforms'].values()
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


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
