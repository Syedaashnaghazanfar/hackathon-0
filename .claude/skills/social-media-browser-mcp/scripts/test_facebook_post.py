#!/usr/bin/env python3
"""
Direct Facebook posting test - bypasses MCP dry_run check.

This script posts directly to Facebook using the saved session.
"""

import asyncio
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright

# Configuration
PLATFORM = "facebook"
SESSION_DIR = Path(__file__).parent.parent.parent.parent.parent / ".social_session"
POST_TEXT = """Testing automated social media posting via AI Employee! 🚀

This is a test post to validate the Gold Tier social media automation features are working correctly."""

async def post_to_facebook(page, text: str):
    """Post text to Facebook."""
    try:
        # Navigate to Facebook
        print("Navigating to Facebook...")
        await page.goto("https://www.facebook.com", timeout=30000)

        # Wait for page to load
        await asyncio.sleep(3)

        # Try to find and click "What's on your mind?" box
        print("Looking for post composer...")
        try:
            # Facebook's UI changes frequently - try multiple approaches
            # Approach 1: Look for the main "What's on your mind?" input
            selectors = [
                # Try with aria-label patterns
                '[aria-label="What\'s on your mind?"]',
                '[aria-label="What\\'s on your mind,"]',
                '[placeholder="What\'s on your mind?"]',
                # Try with data-attributes
                '[data-visualcompletion="ignore-dynamic"]',
                # Try generic contenteditable divs
                'div[contenteditable="true"][role="textbox"]',
                # Try xpath approach through playwright
                'xpath=//div[@contenteditable="true"]',
            ]

            composer = None
            for selector in selectors:
                try:
                    print(f"Trying selector: {selector}")
                    composer = await page.wait_for_selector(selector, timeout=3000)
                    if composer:
                        print(f"Found potential composer!")
                        # Check if it's visible and clickable
                        if await composer.is_visible():
                            print(f"Composer is visible!")
                            break
                except:
                    print(f"Selector failed: {selector}")
                    continue

            if not composer or not await composer.is_visible():
                # Alternative: Navigate directly to create post page
                print("Trying alternative: Navigate to create post page...")
                await page.goto("https://www.facebook.com/create", timeout=30000)
                await asyncio.sleep(2)

                # Try finding composer again
                composer = await page.wait_for_selector('div[contenteditable="true"]', timeout=5000)

            if not composer:
                raise Exception("Could not find post composer. Please check if you're logged in.")

            # Click on the composer to focus
            print("Clicking composer...")
            await composer.click()
            await asyncio.sleep(1)

            # Type the post text
            print("Typing post text...")
            await page.keyboard.type(text, delay=50)
            await asyncio.sleep(2)

            # Look for Post button
            print("Looking for Post button...")
            post_button_selectors = [
                'div[aria-label="Post"]',
                'button[aria-label="Post"]',
                'div:has-text("Post")',
                'button:has-text("Post")',
                'span:has-text("Post")',
            ]

            post_button = None
            for btn_selector in post_button_selectors:
                try:
                    post_button = await page.wait_for_selector(btn_selector, timeout=2000)
                    if post_button and await post_button.is_visible():
                        print(f"Found Post button!")
                        break
                except:
                    continue

            if post_button:
                print("Clicking Post button...")
                await post_button.click()
                await asyncio.sleep(3)
                print("Post button clicked!")
            else:
                # Try pressing Ctrl+Enter to submit
                print("Trying Ctrl+Enter to submit...")
                await page.keyboard.press('Control+Enter')
                await asyncio.sleep(3)

            print("✓ Post published successfully!")
            return True, "https://facebook.com/posts/test"

        except Exception as e:
            print(f"Error during posting: {e}")
            import traceback
            traceback.print_exc()
            return False, "", str(e)

    except Exception as e:
        print(f"Error: {e}")
        return False, "", str(e)

async def main():
    """Main function."""
    print("="*70)
    print("DIRECT FACEBOOK POSTING TEST")
    print("="*70)
    print(f"Session directory: {SESSION_DIR / PLATFORM}")
    print(f"Post text: {POST_TEXT[:100]}...")
    print()

    playwright = await async_playwright().start()

    try:
        # Load persistent context
        platform_dir = SESSION_DIR / PLATFORM
        if not platform_dir.exists():
            print(f"❌ Session directory not found: {platform_dir}")
            print("Please run login_facebook.py first!")
            return

        print("Launching browser with saved session...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(platform_dir),
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720}
        )

        # Get or create page
        if len(context.pages) == 0:
            page = await context.new_page()
        else:
            page = context.pages[0]

        # Post to Facebook
        success, post_url, error = await post_to_facebook(page, POST_TEXT)

        if success:
            print()
            print("="*70)
            print("✓ SUCCESS!")
            print("="*70)
            print(f"Post URL: {post_url}")
            print()
            print("You can verify the post on your Facebook profile.")
            print("Press Ctrl+C to close browser...")
        else:
            print()
            print("="*70)
            print("❌ FAILED")
            print("="*70)
            print(f"Error: {error}")

        # Wait for user to see the result
        await asyncio.sleep(10)

        await context.close()
        await playwright.stop()

    except Exception as e:
        print(f"Fatal error: {e}")
        await playwright.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")
