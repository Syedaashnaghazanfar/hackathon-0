#!/usr/bin/env python3
"""
Facebook Re-authentication Script - Automatic Mode
Opens browser for manual Facebook login and saves session.
"""

import asyncio
import sys
from pathlib import Path

# Add skill directory to path
skill_dir = Path(__file__).parent / ".claude" / "skills" / "social-media-browser-mcp"
sys.path.insert(0, str(skill_dir))

from playwright.async_api import async_playwright

async def reauth_facebook():
    """Re-authenticate Facebook by opening browser for manual login."""
    print("=" * 80)
    print("FACEBOOK RE-AUTHENTICATION")
    print("=" * 80)
    print()

    session_dir = Path(__file__).parent / ".social_session" / "facebook"
    session_dir.mkdir(parents=True, exist_ok=True)

    print("INSTRUCTIONS:")
    print("-" * 80)
    print("1. Browser will open and navigate to Facebook automatically")
    print("2. Log in with your credentials")
    print("3. If asked for 2FA, enter your code")
    print("4. Wait until you see your Facebook home page/news feed")
    print("5. Once fully logged in, CLOSE the browser window")
    print("6. Session will be saved automatically when browser closes")
    print()
    print("Starting browser in 5 seconds...")
    print()

    # Wait 5 seconds before opening
    await asyncio.sleep(5)

    print("[OK] Opening browser...")
    print()

    async with async_playwright() as p:
        # Launch browser with persistent context
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,  # Must be visible for login
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
            ],
            viewport={'width': 1280, 'height': 720},
        )

        # Create new page and navigate to Facebook
        page = await context.new_page()
        await page.goto('https://www.facebook.com', timeout=60000)

        print("[OK] Browser opened! Navigate to: https://www.facebook.com")
        print()
        print("=" * 80)
        print("PLEASE LOG IN NOW")
        print("=" * 80)
        print()
        print("What to do:")
        print("  -> Enter your email/phone and password")
        print("  -> Complete 2FA if required")
        print("  -> Wait for home page to load")
        print("  -> CLOSE the browser window when done")
        print()
        print("Session will be saved when you close the browser.")
        print("Waiting for you to close the browser...")
        print()

        # Wait for browser to be closed by user
        # This will block until the user closes the browser
        try:
            # Keep checking if context is still open
            while context.pages:
                await asyncio.sleep(1)
        except:
            pass

        print()
        print("[OK] Browser closed by user!")
        print()
        print("Verifying session was saved...")

        # Check if session files were created
        session_files = list(session_dir.glob("*"))
        if session_files:
            print(f"[OK] Session saved! Found {len(session_files)} session files")
        else:
            print("[WARNING] No session files found")

        print()
        print("=" * 80)
        print("RE-AUTHENTICATION COMPLETE!")
        print("=" * 80)
        print()
        print("Your Facebook session is now saved.")
        print("Valid for approximately 30 days.")
        print()
        print("Next: Run the test with:")
        print("  python test_social_media_posting.py")
        print()

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  FACEBOOK RE-AUTHENTICATION HELPER")
    print("  Gold Tier AI Employee - Social Media Posting")
    print("=" * 80)
    print()

    asyncio.run(reauth_facebook())
