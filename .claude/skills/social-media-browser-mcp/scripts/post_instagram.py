#!/usr/bin/env python3
"""
Instagram posting - Upload image + caption using saved session.
"""

import asyncio
import sys
from pathlib import Path

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

PLATFORM = "instagram"
SESSION_DIR = Path(__file__).parent.parent.parent.parent.parent / ".social_session"
IMAGE_PATH = Path(__file__).parent.parent.parent.parent.parent / "test_instagram_post.png"
CAPTION = """Testing automated Instagram posting via AI Employee! 🚀

This is a test post to validate Gold Tier automation features. #AI #Automation"""

async def main():
    print("="*70)
    print("INSTAGRAM POSTING - IMAGE + CAPTION")
    print("="*70)
    print(f"\nSession: {SESSION_DIR / PLATFORM}")
    print(f"Image: {IMAGE_PATH}")
    print(f"Caption: {CAPTION[:80]}...")

    if not IMAGE_PATH.exists():
        print(f"\n❌ Image not found: {IMAGE_PATH}")
        return

    playwright = await async_playwright().start()

    try:
        platform_dir = SESSION_DIR / PLATFORM
        if not platform_dir.exists():
            print("❌ Session not found. Run login_instagram.py first!")
            return

        print("\n[1] Launching browser with Instagram session...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(platform_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )

        page = context.pages[0] if context.pages else await context.new_page()

        print("[2] Navigating to Instagram...")
        await page.goto("https://www.instagram.com", timeout=30000)
        await asyncio.sleep(3)

        print("[3] Looking for Create button (+)...")
        try:
            # Instagram create button selectors (multiple strategies)
            create_btn = None

            # Strategy 1: SVG with aria-label
            try:
                create_btn = await page.wait_for_selector('svg[aria-label="New post"]', timeout=5000)
                print("   ✓ Found 'New post' button (SVG)")
            except:
                pass

            # Strategy 2: Look for + icon in nav
            if not create_btn:
                try:
                    create_btn = await page.wait_for_selector('svg:has-text("+")', timeout=3000)
                    print("   ✓ Found + button")
                except:
                    pass

            # Strategy 3: Navigate directly to create URL
            if not create_btn:
                print("   Trying direct navigation to create page...")
                await page.goto("https://www.instagram.com/create", timeout=30000)
                await asyncio.sleep(3)
            else:
                # Click the create button
                await create_btn.click()
                await asyncio.sleep(3)

            print("[4] Looking for file upload button...")
            # Instagram shows a file dialog - we need to handle this
            try:
                # Look for file input
                file_input = await page.wait_for_selector('input[type="file"]', timeout=5000)
                print("   ✓ Found file input")

                print(f"[5] Uploading image: {IMAGE_PATH.name}...")
                await file_input.set_input_files(str(IMAGE_PATH))
                await asyncio.sleep(5)  # Wait for upload

                print("[6] Adding caption...")
                # Look for caption textarea
                try:
                    caption_area = await page.wait_for_selector('textarea[aria-label="Write a caption…"], textarea[placeholder*="caption"], div[contenteditable="true"]', timeout=5000)
                    await caption_area.click()
                    await asyncio.sleep(1)

                    # Type caption
                    await page.keyboard.type(CAPTION, delay=50)
                    await asyncio.sleep(2)
                    print("   ✓ Caption added")
                except:
                    print("   ⚠ Could not find caption area, continuing...")

                print("[7] Looking for Share button...")
                # Look for Share button
                try:
                    share_btn = await page.wait_for_selector('button:has-text("Share"), div[role="button"]:has-text("Share")', timeout=5000)
                    print("   ✓ Found Share button")

                    print("\n🎯 READY TO POST!")
                    print("Browser will stay open for 15 seconds...")
                    print("The post should be ready to share - you can click Share manually if needed.")
                    await asyncio.sleep(15)

                    # Try to click it
                    await share_btn.click()
                    await asyncio.sleep(3)

                    print("\n✓ POST ATTEMPTED!")
                    print("Check your Instagram profile to verify.")

                except:
                    print("\n⚠ Could not find Share button automatically")
                    print("But the image should be uploaded and caption added.")
                    print("Browser staying open for 30 seconds - you can click Share manually!")
                    await asyncio.sleep(30)

            except Exception as e:
                print(f"\n❌ Error during upload: {e}")
                print("\nBrowser staying open for 30 seconds for manual intervention...")
                await asyncio.sleep(30)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(30)

        await context.close()
        await playwright.stop()

    except Exception as e:
        print(f"❌ Fatal: {e}")
        import traceback
        traceback.print_exc()
        await playwright.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped")
