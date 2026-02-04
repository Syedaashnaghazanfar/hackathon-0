"""
Gmail API connection debug script.

Tests Gmail API credentials and token validity.
Helps diagnose authentication issues before running the watcher.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from my_ai_employee.utils.auth_helper import OAuth2Helper
from my_ai_employee.config import get_config
from googleapiclient.discovery import build


def test_credentials_exist():
    """Test if credentials files exist."""
    config = get_config()

    print("=" * 70)
    print("  Gmail API Debug - Credentials Check")
    print("=" * 70)
    print("")

    creds_file = Path(config.gmail_credentials_file)
    token_file = Path(config.gmail_token_file)

    print(f"Credentials file: {creds_file}")
    print(f"  Exists: {creds_file.exists()}")

    if not creds_file.exists():
        print("")
        print("❌ credentials.json NOT FOUND")
        print("")
        print("Setup steps:")
        print("  1. Go to https://console.cloud.google.com/apis/credentials")
        print("  2. Create OAuth 2.0 Client ID (Desktop application)")
        print("  3. Download JSON and save as credentials.json")
        print("  4. Run: uv run python scripts/setup/setup_gmail_oauth.py")
        return False

    print(f"Token file: {token_file}")
    print(f"  Exists: {token_file.exists()}")

    if not token_file.exists():
        print("")
        print("⚠️  token.json NOT FOUND")
        print("")
        print("Setup steps:")
        print("  1. Run: uv run python scripts/setup/setup_gmail_oauth.py")
        print("  2. Browser will open for OAuth consent")
        print("  3. token.json will be saved automatically")
        return False

    print("")
    print("✅ Credentials files exist")
    return True


def test_token_validity():
    """Test if Gmail API token is valid."""
    print("")
    print("=" * 70)
    print("  Gmail API Debug - Token Validation")
    print("=" * 70)
    print("")

    try:
        oauth_helper = OAuth2Helper()
        print("Attempting to get valid credentials...")

        credentials = oauth_helper.get_valid_credentials()

        print("")
        print("✅ Token is valid!")
        print(f"  Token expires: {credentials.expiry}")
        print(f"  Scopes: {credentials.scopes}")

        return True

    except Exception as e:
        print("")
        print(f"❌ Token validation FAILED: {e}")
        print("")
        print("Troubleshooting:")
        print("  1. Token may be expired - re-run setup_gmail_oauth.py")
        print("  2. Credentials may be revoked - check Google Cloud Console")
        print("  3. Check .env GMAIL_CREDENTIALS_FILE and GMAIL_TOKEN_FILE paths")
        return False


def test_gmail_api_connection():
    """Test actual Gmail API connection."""
    print("")
    print("=" * 70)
    print("  Gmail API Debug - API Connection Test")
    print("=" * 70)
    print("")

    try:
        oauth_helper = OAuth2Helper()
        credentials = oauth_helper.get_valid_credentials()

        print("Building Gmail API service...")
        service = build("gmail", "v1", credentials=credentials)

        print("Fetching user profile...")
        profile = service.users().getProfile(userId="me").execute()

        print("")
        print("✅ Gmail API connection successful!")
        print(f"  Email: {profile.get('emailAddress')}")
        print(f"  Messages total: {profile.get('messagesTotal')}")
        print(f"  Threads total: {profile.get('threadsTotal')}")

        # Test fetching messages
        print("")
        print("Testing message fetch...")
        results = service.users().messages().list(
            userId="me",
            maxResults=5,
            q="is:unread"
        ).execute()

        messages = results.get("messages", [])
        print(f"  Found {len(messages)} unread message(s)")

        return True

    except Exception as e:
        print("")
        print(f"❌ Gmail API connection FAILED: {e}")
        print("")
        print("Troubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify Gmail API is enabled in Google Cloud Console")
        print("  3. Check quota limits in Google Cloud Console")
        print("  4. Ensure credentials have 'gmail.modify' scope")
        return False


def main():
    """Main entry point for debug script."""
    print("")
    print("🔍 Gmail API Diagnostic Tool")
    print("")

    # Test 1: Credentials exist
    if not test_credentials_exist():
        print("")
        print("=" * 70)
        print("  RESULT: Credentials files missing")
        print("=" * 70)
        sys.exit(1)

    # Test 2: Token valid
    if not test_token_validity():
        print("")
        print("=" * 70)
        print("  RESULT: Token validation failed")
        print("=" * 70)
        sys.exit(1)

    # Test 3: API connection
    if not test_gmail_api_connection():
        print("")
        print("=" * 70)
        print("  RESULT: API connection failed")
        print("=" * 70)
        sys.exit(1)

    # All tests passed
    print("")
    print("=" * 70)
    print("  RESULT: All tests PASSED ✓")
    print("=" * 70)
    print("")
    print("Gmail watcher is ready to run!")
    print("  Command: uv run python src/my_ai_employee/run_gmail_watcher.py")
    print("")
    sys.exit(0)


if __name__ == "__main__":
    main()
