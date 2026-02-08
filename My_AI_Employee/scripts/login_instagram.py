#!/usr/bin/env python3
"""
Instagram authentication helper for Social Media MCP.

Opens a browser and waits for you to manually log in to Instagram.
Once logged in, the session is saved automatically for future use.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright
import time

# Platform configuration
INSTAGRAM_URL = "https://www.instagram.com"
SESSION_DIR = Path(".social_session/instagram")
CDP_PORT = 9224


def main():
    """Run Instagram authentication flow."""
    print("=" * 60)
    print("Instagram Authentication Helper")
    print("=" * 60)
    print()

    # Create session directory
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Session directory: {SESSION_DIR.absolute()}")
    print()

    print("Starting browser...")
    with sync_playwright() as p:
        # Launch persistent browser
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                f'--remote-debugging-port={CDP_PORT}'
            ],
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(INSTAGRAM_URL, timeout=30000)

        print()
        print("=" * 60)
        print("IMPORTANT: Please log in to Instagram in the browser window")
        print("=" * 60)
        print()
        print("1. Enter your username and password")
        print("2. Complete any 2FA if required")
        print("3. Wait for the Instagram homepage to load")
        print("4. Come back here and press ENTER")
        print()

        input("Press ENTER once you're logged in... ")

        # Verify login
        print()
        print("Verifying login status...")

        try:
            # Check for create post button (indicates logged in)
            page.wait_for_selector('svg[aria-label="New post"]', timeout=10000)
            print()
            print("=" * 60)
            print("SUCCESS: Instagram authentication verified!")
            print("=" * 60)
            print(f"Session saved to: {SESSION_DIR.absolute()}")
            print()
            print("You can now use post_to_instagram() MCP tool.")
            print()

        except Exception as e:
            print()
            print("=" * 60)
            print("WARNING: Could not verify login status")
            print("=" * 60)
            print(f"Error: {e}")
            print()
            print("The session may still be saved. Try using the MCP tool")
            print("to check if authentication worked.")
            print()

        # Close browser
        browser.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("Authentication cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"Error during authentication: {e}")
        sys.exit(1)
