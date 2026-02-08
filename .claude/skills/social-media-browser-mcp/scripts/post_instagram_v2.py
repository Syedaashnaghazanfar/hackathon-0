#!/usr/bin/env python3
"""
Instagram posting v2 - Handle the create post dialog better.
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

Gold Tier automation test! #AI #Automation #Tech"""

async def main():
    print("="*70)
    print("INSTAGRAM POSTING v2 - IMPROVED")
    print("="*70)

    if not IMAGE_PATH.exists():
        print(f"\n❌ Image not found: {IMAGE_PATH}")
        return

    playwright = await async_playwright().start()

    try:
        platform_dir = SESSION_DIR / PLATFORM
        print(f"\n[1] Loading Instagram session from: {platform_dir}")

        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(platform_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )

        page = context.pages[0] if context.pages else await context.new_page()

        print("[2] Navigating to Instagram...")
        await page.goto("https://www.instagram.com", timeout=30000)
        await asyncio.sleep(3)

        print("[3] Clicking Create (+) button...")
        try:
            # Try to find and click the create button
            create_btn = await page.wait_for_selector('svg[aria-label="New post"]', timeout=10000)
            await create_btn.click()
            await asyncio.sleep(3)
            print("   ✓ Clicked")
        except Exception as e:
            print(f"   ⚠ Could not click create button: {e}")

        # After clicking create, a dialog should appear
        print("[4] Looking for upload dialog...")

        # Try to find any file input that appears
        try:
            # Wait a bit for the dialog to appear
            await asyncio.sleep(2)

            # Look for file input (might be in the dialog)
            file_inputs = await page.query_selector_all('input[type="file"]')

            if file_inputs:
                print(f"   ✓ Found {len(file_inputs)} file input(s)")
                # Use the first one
                await file_inputs[0].set_input_files(str(IMAGE_PATH))
                print(f"[5] Upload initiated: {IMAGE_PATH.name}")

                # Wait for upload to process
                await asyncio.sleep(5)

                print("[6] Looking for caption textarea...")
                try:
                    # Instagram might show a "Next" button first
                    try:
                        next_btn = await page.wait_for_selector('button:has-text("Next")', timeout=3000)
                        await next_btn.click()
                        await asyncio.sleep(2)
                        print("   ✓ Clicked Next")
                    except:
                        pass

                    # Now look for caption area
                    caption_selectors = [
                        'textarea[aria-label="Write a caption…"]',
                        'textarea[placeholder*="caption"]',
                        'div[contenteditable="true"]',
                        'textarea',
                    ]

                    caption_area = None
                    for selector in caption_selectors:
                        try:
                            caption_area = await page.wait_for_selector(selector, timeout=2000)
                            if caption_area:
                                print(f"   ✓ Found caption area with: {selector}")
                                break
                        except:
                            continue

                    if caption_area:
                        await caption_area.click()
                        await asyncio.sleep(1)
                        await page.keyboard.type(CAPTION, delay=50)
                        await asyncio.sleep(2)
                        print("   ✓ Caption typed")

                        print("[7] Looking for Share button...")
                        try:
                            # Try multiple share button selectors
                            share_selectors = [
                                'button:has-text("Share")',
                                'div[role="button"]:has-text("Share")',
                                'button:has-text("Share")',
                            ]

                            share_btn = None
                            for selector in share_selectors:
                                try:
                                    share_btn = await page.wait_for_selector(selector, timeout=2000)
                                    if share_btn:
                                        print(f"   ✓ Found Share button")
                                        break
                                except:
                                    continue

                            if share_btn:
                                print("\n🎯 FOUND SHARE BUTTON!")
                                print("Clicking in 3 seconds...")
                                await asyncio.sleep(3)
                                await share_btn.click()
                                await asyncio.sleep(3)
                                print("\n✓ POST CLICKED!")
                                print("\nCheck your Instagram profile!")

                        except Exception as e:
                            print(f"   ⚠ Could not find/click Share button: {e}")
                            print("\nBut caption was added. You can click Share manually!")
                            await asyncio.sleep(30)

                    else:
                        print("   ⚠ Could not find caption area")

                except Exception as e:
                    print(f"   ⚠ Error with caption: {e}")

            else:
                print("   ⚠ No file input found")

                print("\n📸 ALTERNATIVE: Drag and drop")
                print(f"The image is at: {IMAGE_PATH}")
                print("You can manually drag it into the Instagram upload dialog")
                await asyncio.sleep(30)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(30)

        print("\nBrowser will close in 10 seconds...")
        await asyncio.sleep(10)

        await context.close()
        await playwright.stop()

    except Exception as e:
        print(f"❌ Fatal: {e}")
        await asyncio.sleep(30)
        await playwright.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped")
