#!/usr/bin/env python3
"""
Real Facebook Post - Production Post (Not a Test!)
Posts actual content to Facebook with human-like behavior.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add skill directory to path
skill_dir = Path(__file__).parent / ".claude" / "skills" / "social-media-browser-mcp"
sys.path.insert(0, str(skill_dir))

from scripts.social_browser_mcp import SocialMediaBrowser

async def make_real_post():
    """Make a real Facebook post."""
    print("=" * 80)
    print("REAL FACEBOOK POST - PRODUCTION")
    print("=" * 80)
    print()

    # Create a real, meaningful post
    post_text = """EXCITING UPDATE!

I've successfully implemented AI-powered social media automation with human-like behavior!

The system now features:
- Human-like typing patterns (avoids bot detection)
- Smart fallback mechanisms (resilient to UI changes)
- Anti-detection browser configuration
- 100% automated posting

#AI #Automation #Innovation #Technology

This is a real post to demonstrate the system working live!"""

    print(f"Post content:")
    print("-" * 80)
    print(post_text)
    print("-" * 80)
    print()
    print(f"Character count: {len(post_text)}")
    print()

    print(">> What will happen:")
    print("  1. Browser will open with your Facebook session")
    print("  2. Navigate to Facebook homepage")
    print("  3. Click the 'Create Post' trigger")
    print("  4. Type the post with human-like behavior")
    print("  5. Click the 'Post' button automatically")
    print("  6. Keep browser open for 60 seconds so you can verify")
    print()

    print("[*] Starting in 3 seconds (Ctrl+C to cancel)...")
    await asyncio.sleep(3)

    print()
    print("[*] Posting to Facebook now...")
    print("    Watch the browser window to see the magic!")
    print()

    try:
        async with SocialMediaBrowser() as browser:
            print("[OK] Browser started")
            print()

            print("[INFO] Posting to Facebook...")
            print("       Watch the browser window!")
            print()

            success, post_id, error = await browser.post_to_platform(
                'facebook',
                post_text,
                None  # No image for this post
            )

            print()
            print("=" * 80)
            print("POSTING RESULTS")
            print("=" * 80)
            print()

            if success:
                print(">>> SUCCESS! POST PUBLISHED! <<<")
                print()
                print(f"[*] Post ID: {post_id}")
                print(f"[*] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                print(">>> CHECK YOUR FACEBOOK TIMELINE NOW! <<<")
                print("    You should see the post appearing on your profile")
                print()
                print("Post content preview:")
                print("-" * 80)
                print(post_text)
                print("-" * 80)
                print()
                print(">>> SUCCESS! The post is LIVE on your timeline! <<<")
            else:
                print("[X] Posting failed")
                print()
                print(f"[*] Error: {error}")
                print()
                print("[*] The browser window is still open - check what happened")

            print()
            print("=" * 80)
            print("[*] Browser will stay open for 60 seconds...")
            print("    Verify the post on your Facebook timeline!")
            print("=" * 80)
            print()

            # Keep browser open for verification
            await asyncio.sleep(60)

            print()
            print("[OK] Complete! Check your Facebook timeline.")

    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print()
        print(f"[!] Exception: {e}")
        print()
        print("Check if:")
        print("  - Session is still valid")
        print("  - Internet connection is working")
        print("  - Facebook is accessible")

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  >> REAL FACEBOOK POST <<")
    print("  Production Posting - Not a Test!")
    print("=" * 80)
    print()

    asyncio.run(make_real_post())
