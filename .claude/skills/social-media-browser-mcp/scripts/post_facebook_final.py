#!/usr/bin/env python3
"""
Facebook posting - Use the create page directly (more reliable).
"""

import asyncio
import sys
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

PLATFORM = "facebook"
SESSION_DIR = Path(__file__).parent.parent.parent.parent.parent / ".social_session"
POST_TEXT = """Testing automated social media posting via AI Employee! 🚀

This is a test to validate Gold Tier automation."""

async def main():
    print("="*70)
    print("FACEBOOK POSTING - CREATE PAGE METHOD")
    print("="*70)

    playwright = await async_playwright().start()

    try:
        platform_dir = SESSION_DIR / PLATFORM
        if not platform_dir.exists():
            print("❌ Session not found. Run login_facebook.py first!")
            return

        print("\n[1] Launching browser with session...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(platform_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )

        page = context.pages[0] if context.pages else await context.new_page()

        print("[2] Navigating to Facebook create page...")
        await page.goto("https://www.facebook.com/create", timeout=30000)
        await asyncio.sleep(3)

        print("[3] Looking for composer box...")
        # On create page, there's usually a simple text area
        try:
            # Try multiple selector strategies
            composer = None

            # Strategy 1: Look for any contenteditable div
            try:
                composer = await page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
                print("   ✓ Found contenteditable div")
            except:
                pass

            # Strategy 2: Look for textarea
            if not composer:
                try:
                    composer = await page.wait_for_selector('textarea', timeout=3000)
                    print("   ✓ Found textarea")
                except:
                    pass

            # Strategy 3: Look for role="textbox"
            if not composer:
                try:
                    composer = await page.wait_for_selector('[role="textbox"]', timeout=3000)
                    print("   ✓ Found textbox")
                except:
                    pass

            if not composer:
                print("❌ Could not find composer")
                print("   Keeping browser open for 30 seconds for manual inspection...")
                await asyncio.sleep(30)
                return

            # Click to focus
            await composer.click()
            await asyncio.sleep(1)

            print("[4] Typing post content...")
            # Select all and type
            await page.keyboard.press('Control+A')
            await asyncio.sleep(0.3)
            await page.keyboard.type(POST_TEXT, delay=100)
            await asyncio.sleep(2)

            print("[5] Submitting post...")
            # Try Ctrl+Enter to submit
            await page.keyboard.press('Control+Enter')
            await asyncio.sleep(3)

            # Also try plain Enter
            await page.keyboard.press('Enter')
            await asyncio.sleep(3)

            print("\n✓ Post attempted!")
            print("\nPLEASE CHECK YOUR FACEBOOK PROFILE to verify.")
            print("\nBrowser will stay open for 20 seconds...")
            await asyncio.sleep(20)

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(30)

        await context.close()
        await playwright.stop()

    except Exception as e:
        print(f"❌ Fatal: {e}")
        await playwright.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped")
