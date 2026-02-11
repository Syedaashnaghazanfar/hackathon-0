#!/usr/bin/env python3
"""Quick check if Facebook session is working."""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def quick_check():
    session_dir = Path(".social_session/facebook")

    print("Checking Facebook session...")
    print(f"Session exists: {session_dir.exists()}")
    print()

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            headless=False,
        )

        if len(context.pages) == 0:
            page = await context.new_page()
        else:
            page = context.pages[0]

        print("Navigating to Facebook...")
        try:
            await page.goto('https://www.facebook.com', timeout=60000)
            print("[OK] Facebook loaded successfully!")

            title = await page.title()
            print(f"Page title: {title}")

            await asyncio.sleep(30)
            print("[OK] Session is working - ready to post!")

        except Exception as e:
            print(f"[X] Error: {e}")
            print("[X] May need re-authentication")

        await context.close()

if __name__ == "__main__":
    asyncio.run(quick_check())
