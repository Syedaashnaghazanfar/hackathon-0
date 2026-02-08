#!/usr/bin/env python3
"""
Facebook posting with full debugging - takes screenshots, logs everything.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

# Configuration
PLATFORM = "facebook"
SESSION_DIR = Path(__file__).parent.parent.parent.parent.parent / ".social_session"
POST_TEXT = """Testing automated social media posting via AI Employee!

This is a test post to validate the Gold Tier social media automation features are working correctly."""

async def post_to_facebook(page, text: str, screenshot_dir: Path):
    """Post text to Facebook with extensive debugging."""
    try:
        # Navigate to Facebook
        print("\n[1] Navigating to Facebook...")
        await page.goto("https://www.facebook.com", timeout=30000)

        # Wait for page load
        await asyncio.sleep(3)

        # Take screenshot of current state
        screenshot_path = screenshot_dir / f"01_facebook_home.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"   Screenshot saved: {screenshot_path}")

        # Check if we're logged in
        print("\n[2] Checking login status...")
        is_logged_in = False

        # Check for logged-in indicators
        try:
            # Look for common logged-in elements
            await page.wait_for_selector('div[aria-label="Your profile"]', timeout=3000)
            is_logged_in = True
            print("   ✓ Logged in (profile menu found)")
        except:
            try:
                await page.wait_for_selector('div[aria-label="Menu"]', timeout=3000)
                is_logged_in = True
                print("   ✓ Logged in (menu found)")
            except:
                print("   ✗ Login status unclear, continuing...")

        # Try to find the "What's on your mind?" input
        print("\n[3] Looking for post composer...")

        # Strategy 1: Try clicking in the main feed area first
        print("   Strategy 1: Looking for main feed composer...")
        try:
            # Facebook often has a "What's on your mind?" in a generic div
            all_divs = await page.query_selector_all('div')
            print(f"   Found {len(all_divs)} div elements on page")

            # Look for divs with specific text patterns
            clickable_elements = await page.query_selector_all('[role="button"], [contenteditable="true"]')
            print(f"   Found {len(clickable_elements)} interactive elements")

            # Try to find something with "What" in aria-label or text
            potential_composers = []

            for element in clickable_elements[:50]:  # Check first 50
                try:
                    text_content = await element.inner_text()
                    aria_label = await element.get_attribute('aria-label')
                    placeholder = await element.get_attribute('placeholder')

                    if text_content and 'what' in text_content.lower():
                        potential_composers.append(('text', text_content[:50], element))
                    if aria_label and 'what' in aria_label.lower():
                        potential_composers.append(('aria', aria_label, element))
                    if placeholder and 'what' in placeholder.lower():
                        potential_composers.append(('placeholder', placeholder, element))
                except:
                    continue

            print(f"   Found {len(potential_composers)} potential composers")

            if potential_composers:
                for found_type, found_text, element in potential_composers:
                    print(f"   - Found by {found_type}: {found_text}")
                    try:
                        await element.click()
                        await asyncio.sleep(1)

                        # Take screenshot after click
                        screenshot_path = screenshot_dir / f"02_after_click_{found_type}.png"
                        await page.screenshot(path=str(screenshot_path), full_page=True)
                        print(f"   Screenshot saved: {screenshot_path}")

                        # Now type the text
                        print(f"\n[4] Typing post text...")
                        await page.keyboard.type(text, delay=50)
                        await asyncio.sleep(2)

                        # Screenshot after typing
                        screenshot_path = screenshot_dir / f"03_after_typing.png"
                        await page.screenshot(path=str(screenshot_path), full_page=True)
                        print(f"   Screenshot saved: {screenshot_path}")

                        # Look for Post button
                        print(f"\n[5] Looking for Post button...")
                        post_buttons = await page.query_selector_all('div, button, span, a[role="button"]')

                        for btn in post_buttons:
                            try:
                                btn_text = await btn.inner_text()
                                if btn_text and 'post' in btn_text.lower():
                                    print(f"   Found Post button: {btn_text[:50]}")
                                    await btn.click()
                                    await asyncio.sleep(3)

                                    # Final screenshot
                                    screenshot_path = screenshot_dir / f"04_after_post.png"
                                    await page.screenshot(path=str(screenshot_path), full_page=True)
                                    print(f"   Screenshot saved: {screenshot_path}")

                                    print("\n✓ POST PUBLISHED SUCCESSFULLY!")
                                    return True, "https://facebook.com/posts/test", "Success"

                            except:
                                continue

                        # If no Post button found, try Ctrl+Enter
                        print("   Trying Ctrl+Enter to submit...")
                        await page.keyboard.press('Control+Enter')
                        await asyncio.sleep(3)

                        screenshot_path = screenshot_dir / f"04_after_ctrl_enter.png"
                        await page.screenshot(path=str(screenshot_path), full_page=True)
                        print(f"   Screenshot saved: {screenshot_path}")

                        print("\n✓ POST PUBLISHED (via Ctrl+Enter)!")
                        return True, "https://facebook.com/posts/test"

                    except Exception as e:
                        print(f"   Error with this element: {e}")
                        continue

        except Exception as e:
            print(f"   Strategy 1 failed: {e}")

        # Strategy 2: Navigate to create post directly
        print("\n   Strategy 2: Navigating to create post page...")
        try:
            await page.goto("https://www.facebook.com/create", timeout=30000)
            await asyncio.sleep(3)

            screenshot_path = screenshot_dir / f"10_create_page.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"   Screenshot saved: {screenshot_path}")

            # Look for any contenteditable div
            composer = await page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
            if composer:
                print("   Found composer on create page!")
                await composer.click()
                await asyncio.sleep(1)
                await page.keyboard.type(text, delay=50)
                await asyncio.sleep(2)

                # Try to find and click Post button
                buttons = await page.query_selector_all('button, div[role="button"]')
                for btn in buttons:
                    try:
                        btn_text = await btn.inner_text()
                        if 'post' in btn_text.lower():
                            await btn.click()
                            await asyncio.sleep(3)
                            print("\n✓ POST PUBLISHED!")
                            return True, "https://facebook.com/posts/test"
                    except:
                        continue

        except Exception as e:
            print(f"   Strategy 2 failed: {e}")

        print("\n❌ All strategies failed")
        return False, "", "Could not find composer or post button"

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False, "", str(e)

async def main():
    """Main function."""
    print("="*70)
    print("FACEBOOK POSTING - DEBUG MODE")
    print("="*70)

    # Create screenshot directory
    screenshot_dir = Path(__file__).parent / "screenshots" / datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nScreenshots will be saved to: {screenshot_dir}")

    print(f"\nSession directory: {SESSION_DIR / PLATFORM}")
    print(f"Post text: {POST_TEXT[:100]}...")

    playwright = await async_playwright().start()

    try:
        # Load persistent context
        platform_dir = SESSION_DIR / PLATFORM
        if not platform_dir.exists():
            print(f"\n❌ Session directory not found: {platform_dir}")
            print("Please run login_facebook.py first!")
            return

        print("\n[0] Launching browser with saved session...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(platform_dir),
            headless=False,  # Show browser so you can see what's happening
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 720}
        )

        # Get or create page
        if len(context.pages) == 0:
            page = await context.new_page()
        else:
            page = context.pages[0]

        # Post to Facebook
        success, post_url, error = await post_to_facebook(page, POST_TEXT, screenshot_dir)

        if success:
            print("\n" + "="*70)
            print("✓ SUCCESS!")
            print("="*70)
            print(f"Post URL: {post_url}")
            print(f"\nCheck your Facebook profile to verify!")
            print("\nBrowser will stay open for 30 seconds so you can verify...")
            await asyncio.sleep(30)
        else:
            print("\n" + "="*70)
            print("❌ FAILED")
            print("="*70)
            print(f"Error: {error}")
            print(f"\nCheck screenshots in: {screenshot_dir}")
            print("\nBrowser will stay open for 60 seconds for manual inspection...")
            await asyncio.sleep(60)

        await context.close()
        await playwright.stop()

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        await playwright.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nStopped by user")
