#!/usr/bin/env python3
"""
Twitter/X authentication helper for Social Media MCP.

Opens a browser and waits for you to manually log in to Twitter/X.
Once logged in, the session is saved automatically for future use.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright
import time

# Platform configuration
TWITTER_URL = "https://x.com"
SESSION_DIR = Path(".social_session/twitter")
CDP_PORT = 9225


def main():
    """Run Twitter/X authentication flow."""
    print("=" * 60)
    print("Twitter/X Authentication Helper")
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
        page.goto(TWITTER_URL, timeout=30000)

        print()
        print("=" * 60)
        print("IMPORTANT: Please log in to Twitter/X in the browser window")
        print("=" * 60)
        print()
        print("1. Enter your username/email and password")
        print("2. Complete any 2FA if required")
        print("3. Wait for the Twitter homepage to load")
        print("4. Come back here and press ENTER")
        print()

        input("Press ENTER once you're logged in... ")

        # Verify login
        print()
        print("Verifying login status...")

        try:
            # Check for tweet box (indicates logged in)
            page.wait_for_selector('div[contenteditable="true"][data-text]', timeout=10000)
            print()
            print("=" * 60)
            print("SUCCESS: Twitter/X authentication verified!")
            print("=" * 60)
            print(f"Session saved to: {SESSION_DIR.absolute()}")
            print()
            print("You can now use post_to_twitter() MCP tool.")
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
