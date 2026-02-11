#!/usr/bin/env python3
"""
Simple test to verify Facebook session works
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def test_session():
    """Test if Facebook session works."""
    session_dir = Path(".social_session/facebook")

    print("=" * 80)
    print("TESTING FACEBOOK SESSION")
    print("=" * 80)
    print()

    print(f"Session directory: {session_dir.absolute()}")
    print(f"Session exists: {session_dir.exists()}")
    print()

    async with async_playwright() as p:
        print("Launching browser with persistent context...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
            ],
            viewport={'width': 1280, 'height': 720},
        )

        print("[OK] Browser launched")
        print()

        if len(context.pages) == 0:
            page = await context.new_page()
        else:
            page = context.pages[0]

        print("Navigating to Facebook...")
        await page.goto('https://www.facebook.com', timeout=30000)

        print("[OK] Page loaded")
        print()

        # Check page title
        title = await page.title()
        print(f"Page title: {title}")
        print()

        # Check URL
        url = page.url
        print(f"Current URL: {url}")
        print()

        # Check if logged in by looking for login form
        has_login_form = False
        try:
            await page.wait_for_selector('input[name="email"]', timeout=3000)
            has_login_form = True
            print("[X] Found login form - NOT LOGGED IN")
        except:
            print("[OK] No login form found - appears to be logged in")

        print()

        # Check for post composer
        try:
            await page.wait_for_selector('div[contenteditable="true"]', timeout=5000)
            print("[OK] Found post composer - CONFIRMED LOGGED IN")
        except:
            print("[?] Post composer not found (UI may have changed)")

        print()
        print("=" * 80)
        print("Browser will stay open for 30 seconds")
        print("Check if you can see your Facebook home page")
        print("=" * 80)
        print()

        await asyncio.sleep(30)

        await context.close()
        print()
        print("[OK] Test complete!")

if __name__ == "__main__":
    asyncio.run(test_session())
