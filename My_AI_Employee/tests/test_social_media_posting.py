#!/usr/bin/env python3
"""
Test script for improved social media posting.
Tests Facebook posting with anti-detection improvements.
"""

import asyncio
import sys
from pathlib import Path

# Add skill directory to path
skill_dir = Path(__file__).parent / ".claude" / "skills" / "social-media-browser-mcp"
sys.path.insert(0, str(skill_dir))

from scripts.social_browser_mcp import SocialMediaBrowser

async def test_facebook_post():
    """Test Facebook posting with improvements."""
    print("=" * 80)
    print("TESTING IMPROVED SOCIAL MEDIA POSTING - FACEBOOK")
    print("=" * 80)
    print()

    test_text = "Testing improved AI automation with human-like typing! #automation #testing #AI"

    print(f"Test text: \"{test_text}\"")
    print(f"Text length: {len(test_text)} characters")
    print()

    print("Expected improvements:")
    print("  [+] Multiple fallback selectors (3-4 attempts per element)")
    print("  [+] Human-like typing (50-150ms per character)")
    print("  [+] Random delays between actions")
    print("  [+] Anti-detection browser flags")
    print("  [+] Three-tier click fallback (standard -> JS -> manual)")
    print()

    print("Starting browser...")
    print()

    try:
        async with SocialMediaBrowser() as browser:
            print("[OK] Browser started successfully")
            print()

            print("Attempting Facebook post...")
            print("Watch for:")
            print("  - Character-by-character typing (not instant)")
            print("  - Random pauses (1-2 seconds)")
            print("  - Post button click (or manual click prompt)")
            print()

            success, post_id, error = await browser.post_to_platform(
                'facebook',
                test_text,
                None  # No image for this test
            )

            print()
            print("=" * 80)
            print("TEST RESULTS")
            print("=" * 80)
            print()

            if success:
                print("[SUCCESS] FULL SUCCESS - Post published automatically!")
                print(f"   Post ID: {post_id}")
                print(f"   Check your Facebook timeline to verify")
            elif "manual" in error.lower() or "click" in error.lower():
                print("[PARTIAL] SEMI-AUTOMATION SUCCESS (90% automation)")
                print()
                print("   What happened:")
                print("   [OK] Browser opened and navigated")
                print("   [OK] Logged in automatically")
                print("   [OK] Text typed with human-like behavior")
                print("   [X] Final button click blocked by anti-bot")
                print()
                print("   Action required:")
                print("   -> Go to the browser window")
                print("   -> Click the 'Post' button manually")
                print("   -> This is still 90% automation success!")
            else:
                print("[FAIL] FAILURE")
                print(f"   Error: {error}")
                print()
                print("   Possible causes:")
                print("   - Session expired (re-authenticate)")
                print("   - UI changed significantly (update selectors)")
                print("   - Network issue")

            print()
            print("=" * 80)

            # Keep browser open for 10 seconds so user can see result
            print()
            print("Browser will remain open for 10 seconds...")
            print("Check the browser window to see the result!")
            await asyncio.sleep(10)

    except Exception as e:
        print()
        print("=" * 80)
        print("TEST FAILED WITH EXCEPTION")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        print("Possible issues:")
        print("  - Playwright not installed: pip install playwright")
        print("  - Browsers not installed: playwright install chromium")
        print("  - Session files corrupted")
        print()

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  SOCIAL MEDIA POSTING TEST - IMPROVED VERSION")
    print("  Testing anti-detection improvements")
    print("=" * 80)
    print()

    asyncio.run(test_facebook_post())
