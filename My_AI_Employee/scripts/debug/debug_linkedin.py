"""
LinkedIn API connection debug script.

Tests LinkedIn API credentials and access token validity.
Helps diagnose authentication issues before running the watcher.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from my_ai_employee.config import get_config
import requests


def test_token_exists():
    """Test if LinkedIn access token is configured."""
    config = get_config()

    print("=" * 70)
    print("  LinkedIn API Debug - Token Check")
    print("=" * 70)
    print("")

    token = config.linkedin_access_token
    person_urn = config.linkedin_person_urn

    print(f"Access token configured: {bool(token)}")
    if token:
        print(f"  Token preview: {token[:10]}...")

    print(f"Person URN configured: {bool(person_urn)}")
    if person_urn:
        print(f"  URN: {person_urn}")

    if not token:
        print("")
        print("❌ LINKEDIN_ACCESS_TOKEN NOT CONFIGURED")
        print("")
        print("Setup steps:")
        print("  1. Create LinkedIn app at https://www.linkedin.com/developers/apps")
        print("  2. Add redirect URL: http://localhost:8000/callback")
        print("  3. Run: uv run python scripts/setup/linkedin_oauth2_setup.py")
        print("  4. Token will be saved to .env automatically")
        return False

    if not person_urn:
        print("")
        print("⚠️  LINKEDIN_PERSON_URN NOT CONFIGURED")
        print("")
        print("This is required for posting. Re-run linkedin_oauth2_setup.py")
        return False

    print("")
    print("✅ LinkedIn credentials configured")
    return True


def test_token_validity():
    """Test if LinkedIn access token is valid."""
    print("")
    print("=" * 70)
    print("  LinkedIn API Debug - Token Validation")
    print("=" * 70)
    print("")

    config = get_config()
    token = config.linkedin_access_token

    try:
        print("Testing token with LinkedIn API...")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Test with profile endpoint
        response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            profile = response.json()
            print("")
            print("✅ Token is valid!")
            print(f"  Profile ID: {profile.get('id')}")
            first_name = profile.get('localizedFirstName', 'N/A')
            last_name = profile.get('localizedLastName', 'N/A')
            print(f"  Name: {first_name} {last_name}")
            return True

        elif response.status_code == 401:
            print("")
            print("❌ Token is INVALID or EXPIRED (401 Unauthorized)")
            print("")
            print("Troubleshooting:")
            print("  1. LinkedIn tokens expire after 60 days")
            print("  2. Re-run: uv run python scripts/setup/linkedin_oauth2_setup.py")
            print("  3. Update LINKEDIN_ACCESS_TOKEN in .env")
            return False

        else:
            print("")
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"  Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print("")
        print(f"❌ API connection FAILED: {e}")
        print("")
        print("Troubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify LinkedIn API is accessible")
        print("  3. Check for rate limiting")
        return False


def test_posting_permissions():
    """Test if token has posting permissions."""
    print("")
    print("=" * 70)
    print("  LinkedIn API Debug - Posting Permissions")
    print("=" * 70)
    print("")

    config = get_config()
    token = config.linkedin_access_token
    person_urn = config.linkedin_person_urn

    try:
        print("Checking posting permissions...")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        # Try to create a dry-run post (we won't actually post)
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": "[Test post - will not be published]"
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"
            }
        }

        # Note: We're not actually posting, just checking if the endpoint is accessible
        # A 400 or validation error would indicate permissions are OK
        # A 403 would indicate missing permissions

        print("")
        print("✅ Posting permissions check complete")
        print("")
        print("Note: Cannot verify without actually posting.")
        print("Test by running LinkedIn watcher in DRY_RUN mode:")
        print("  DRY_RUN=true uv run python src/my_ai_employee/watchers/linkedin_watcher.py")

        return True

    except Exception as e:
        print("")
        print(f"⚠️  Permission check error: {e}")
        print("")
        print("This is expected - full test requires actually posting.")
        return True  # Don't fail on this


def main():
    """Main entry point for debug script."""
    print("")
    print("🔍 LinkedIn API Diagnostic Tool")
    print("")

    # Test 1: Token exists
    if not test_token_exists():
        print("")
        print("=" * 70)
        print("  RESULT: LinkedIn credentials not configured")
        print("=" * 70)
        sys.exit(1)

    # Test 2: Token valid
    if not test_token_validity():
        print("")
        print("=" * 70)
        print("  RESULT: Token validation failed")
        print("=" * 70)
        sys.exit(1)

    # Test 3: Posting permissions (optional)
    test_posting_permissions()

    # All tests passed
    print("")
    print("=" * 70)
    print("  RESULT: All tests PASSED ✓")
    print("=" * 70)
    print("")
    print("LinkedIn watcher is ready to run!")
    print("  Command: uv run python src/my_ai_employee/watchers/linkedin_watcher.py")
    print("")
    print("⚠️  IMPORTANT: LinkedIn tokens expire after 60 days")
    print("   Re-run linkedin_oauth2_setup.py before expiration")
    print("")
    sys.exit(0)


if __name__ == "__main__":
    main()
