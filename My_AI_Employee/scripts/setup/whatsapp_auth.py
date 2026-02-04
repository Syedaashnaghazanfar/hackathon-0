#!/usr/bin/env python3
"""
WhatsApp Web authentication script for Silver Tier AI Employee.

Runs interactive browser automation:
1. Launches headless Chrome with WhatsApp Web
2. Displays QR code in terminal
3. User scans with WhatsApp mobile app
4. Saves session to .whatsapp_session/ directory
"""

import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    """Run WhatsApp Web authentication."""
    print("=" * 60)
    print("WhatsApp Web Authentication for Silver Tier AI Employee")
    print("=" * 60)
    print()

    # Session directory
    session_dir = os.getenv("WHATSAPP_SESSION_DIR", ".whatsapp_session")
    session_path = Path(session_dir)

    # Check if session already exists
    if session_path.exists() and any(session_path.iterdir()):
        print(f"✓ Existing session found in {session_dir}")
        print()
        overwrite = input("Re-authenticate (existing session will be deleted)? (y/N): ").strip().lower()
        if overwrite != "y":
            print("Keeping existing session. Exiting.")
            return

        # Delete existing session
        import shutil
        shutil.rmtree(session_path)
        print(f"✓ Deleted existing session")
        print()

    # Create session directory
    session_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Step 1: Launch WhatsApp Web")
    print("=" * 60)
    print()
    print("Launching browser...")
    print()

    with sync_playwright() as p:
        # Launch browser with persistent context (saves session)
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=False,  # Show browser for QR scan
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
            ],
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        # Navigate to WhatsApp Web
        print("Opening WhatsApp Web...")
        page.goto("https://web.whatsapp.com")

        print()
        print("=" * 60)
        print("Step 2: Scan QR Code")
        print("=" * 60)
        print()
        print("Instructions:")
        print("1. Open WhatsApp on your mobile device")
        print("2. Go to Settings > Linked Devices")
        print("3. Tap 'Link a Device'")
        print("4. Scan the QR code shown in the browser window")
        print()
        print("Waiting for QR code scan...")
        print()

        try:
            # Wait for successful login (chats page loads)
            page.wait_for_selector("div[data-testid='chat']", timeout=120000)  # 2 minutes

            print()
            print("=" * 60)
            print("✓ WhatsApp Web authenticated successfully!")
            print("=" * 60)
            print()

            # Wait a bit for session to fully persist
            print("Saving session...")
            time.sleep(5)

        except Exception as e:
            print()
            print("=" * 60)
            print("ERROR: Authentication failed")
            print("=" * 60)
            print()
            print(f"Reason: {e}")
            print()
            print("Please try again:")
            print("  uv run python scripts/setup/whatsapp_auth.py")
            print()
            browser.close()
            sys.exit(1)

        # Close browser
        browser.close()

    print(f"✓ Session saved to {session_dir}")
    print()
    print("You can now use the WhatsApp watcher:")
    print("  uv run python -m my_ai_employee.watchers.whatsapp_watcher")
    print()
    print("IMPORTANT: Session may expire after ~2 weeks of inactivity.")
    print("Re-run this script if the watcher fails to connect.")
    print()


if __name__ == "__main__":
    main()
