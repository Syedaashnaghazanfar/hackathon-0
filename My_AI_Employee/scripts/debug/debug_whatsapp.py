"""
WhatsApp Web session debug script.

Tests WhatsApp Web session authentication and Playwright setup.
Helps diagnose authentication issues before running the watcher.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from my_ai_employee.config import get_config


def test_session_exists():
    """Test if WhatsApp session directory exists."""
    config = get_config()

    print("=" * 70)
    print("  WhatsApp Web Debug - Session Check")
    print("=" * 70)
    print("")

    session_dir = Path(config.whatsapp_session_dir)

    print(f"Session directory: {session_dir}")
    print(f"  Exists: {session_dir.exists()}")

    if not session_dir.exists():
        print("")
        print("⚠️  WhatsApp session NOT FOUND")
        print("")
        print("Setup steps:")
        print("  1. Run: uv run python scripts/setup/whatsapp_auth.py")
        print("  2. Browser will open with QR code")
        print("  3. Scan QR with WhatsApp mobile app")
        print("  4. Session will be saved automatically")
        print("")
        print("Note: Session expires every ~2 weeks, re-run to refresh")
        return False

    # Check session files
    session_files = list(session_dir.glob("*"))
    print(f"  Files: {len(session_files)}")

    if len(session_files) == 0:
        print("")
        print("❌ Session directory is EMPTY")
        print("")
        print("Re-run whatsapp_auth.py to create session")
        return False

    print("")
    print("✅ WhatsApp session exists")
    print("")
    print("⚠️  Session may be expired. Test with watcher to verify.")
    return True


def test_playwright_installed():
    """Test if Playwright is installed."""
    print("")
    print("=" * 70)
    print("  WhatsApp Web Debug - Playwright Check")
    print("=" * 70)
    print("")

    try:
        from playwright.sync_api import sync_playwright

        print("Playwright import: ✅")

        # Test browser installation
        print("")
        print("Testing Chromium browser...")

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()

                print("  Chromium installed: ✅")
                print("")
                print("✅ Playwright is ready")
                return True

            except Exception as e:
                print("")
                print(f"❌ Chromium NOT installed: {e}")
                print("")
                print("Setup steps:")
                print("  Run: playwright install chromium")
                print("")
                return False

    except ImportError:
        print("")
        print("❌ Playwright NOT installed")
        print("")
        print("Setup steps:")
        print("  1. Run: uv add playwright")
        print("  2. Run: playwright install chromium")
        print("")
        return False


def test_whatsapp_connection():
    """Test WhatsApp Web connection with session."""
    print("")
    print("=" * 70)
    print("  WhatsApp Web Debug - Connection Test")
    print("=" * 70)
    print("")

    config = get_config()
    session_dir = Path(config.whatsapp_session_dir)

    if not session_dir.exists():
        print("❌ Session not found, skipping connection test")
        return False

    try:
        from playwright.sync_api import sync_playwright

        print("Attempting to load WhatsApp Web with saved session...")
        print("(This will open a browser window)")
        print("")

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,  # Show browser for debugging
                timeout=30000,
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://web.whatsapp.com", timeout=30000)

            print("Waiting for WhatsApp Web to load (30 seconds)...")
            print("")

            # Wait for either QR code or chat list
            try:
                # If chat list appears, we're authenticated
                page.wait_for_selector('div[aria-label="Chat list"]', timeout=30000)

                print("")
                print("✅ WhatsApp Web connection successful!")
                print("  Session is valid and authenticated")
                print("")

                browser.close()
                return True

            except Exception:
                # Check if QR code appeared (session expired)
                try:
                    page.wait_for_selector('canvas[aria-label*="QR"]', timeout=5000)

                    print("")
                    print("⚠️  QR code detected - Session has EXPIRED")
                    print("")
                    print("Action required:")
                    print("  1. Re-run: uv run python scripts/setup/whatsapp_auth.py")
                    print("  2. Scan new QR code with WhatsApp mobile app")
                    print("")

                    browser.close()
                    return False

                except Exception:
                    print("")
                    print("⚠️  Could not determine WhatsApp Web state")
                    print("")
                    print("Please check browser window manually:")
                    print("  - If you see QR code: Session expired, re-run whatsapp_auth.py")
                    print("  - If you see chat list: Session is valid")
                    print("")
                    print("Press Enter to close browser...")
                    input()

                    browser.close()
                    return False

    except Exception as e:
        print("")
        print(f"❌ Connection test FAILED: {e}")
        print("")
        print("Troubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify WhatsApp mobile app is online")
        print("  3. Re-run whatsapp_auth.py to refresh session")
        return False


def main():
    """Main entry point for debug script."""
    print("")
    print("🔍 WhatsApp Web Diagnostic Tool")
    print("")

    # Test 1: Session exists
    session_exists = test_session_exists()

    # Test 2: Playwright installed
    if not test_playwright_installed():
        print("")
        print("=" * 70)
        print("  RESULT: Playwright not installed")
        print("=" * 70)
        sys.exit(1)

    if not session_exists:
        print("")
        print("=" * 70)
        print("  RESULT: Session not found")
        print("=" * 70)
        print("")
        print("Run whatsapp_auth.py to create session first")
        sys.exit(1)

    # Test 3: Connection test (optional - requires user interaction)
    print("")
    print("Would you like to test the WhatsApp Web connection?")
    print("(This will open a browser window)")
    response = input("Test connection? (y/n): ").strip().lower()

    if response == 'y':
        if not test_whatsapp_connection():
            print("")
            print("=" * 70)
            print("  RESULT: Connection test failed")
            print("=" * 70)
            sys.exit(1)

    # All tests passed
    print("")
    print("=" * 70)
    print("  RESULT: All tests PASSED ✓")
    print("=" * 70)
    print("")
    print("WhatsApp watcher is ready to run!")
    print("  Command: uv run python src/my_ai_employee/watchers/whatsapp_watcher.py")
    print("")
    print("⚠️  IMPORTANT: Session expires every ~2 weeks")
    print("   Re-run whatsapp_auth.py before expiration")
    print("")
    sys.exit(0)


if __name__ == "__main__":
    main()
