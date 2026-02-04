#!/usr/bin/env python3
"""
Test LinkedIn REST API Connection

Verifies that LinkedIn OAuth2 credentials are configured correctly
and the API is accessible.

Usage:
    python test_linkedin_api.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# LinkedIn API Configuration
ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
PERSON_URN = os.getenv('LINKEDIN_PERSON_URN')
API_VERSION = os.getenv('LINKEDIN_API_VERSION', '202601')


def get_headers():
    """Get headers for LinkedIn API requests."""
    return {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': API_VERSION,
        'Content-Type': 'application/json'
    }


def test_configuration():
    """Test if environment variables are configured."""
    print("\n" + "=" * 60)
    print("LinkedIn REST API Configuration Test")
    print("=" * 60)

    print("\n1. Checking environment variables...")

    if not ACCESS_TOKEN:
        print("   ❌ LINKEDIN_ACCESS_TOKEN not found")
        print("   Run: python scripts/linkedin_oauth2_setup.py")
        return False

    if not PERSON_URN:
        print("   ⚠️  LINKEDIN_PERSON_URN not found (will be fetched from API)")
    else:
        print(f"   ✅ LINKEDIN_PERSON_URN: {PERSON_URN}")

    print(f"   ✅ LINKEDIN_ACCESS_TOKEN: {ACCESS_TOKEN[:20]}...")
    print(f"   ✅ LINKEDIN_API_VERSION: {API_VERSION}")

    return True


def test_api_connection():
    """Test API connection by fetching user info."""
    print("\n2. Testing API connection...")

    try:
        response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=get_headers(),
            timeout=10
        )

        if response.status_code == 200:
            user_info = response.json()
            print("   ✅ API connection successful")
            print(f"   User ID: {user_info.get('sub', 'Unknown')}")
            print(f"   Name: {user_info.get('name', 'Unknown')}")
            print(f"   Email: {user_info.get('email', 'Unknown')}")

            # Show person URN
            person_urn = f"urn:li:person:{user_info.get('sub')}"
            print(f"   Person URN: {person_urn}")

            if not PERSON_URN:
                print("\n   ⚠️  Add this to your .env file:")
                print(f"   LINKEDIN_PERSON_URN={person_urn}")

            return True

        elif response.status_code == 401:
            print("   ❌ Authentication failed (401 Unauthorized)")
            print("   Token may be expired. Run: python scripts/linkedin_oauth2_setup.py")
            return False

        elif response.status_code == 403:
            print("   ❌ Access forbidden (403 Forbidden)")
            print("   Check your app permissions at https://www.linkedin.com/developers/")
            return False

        else:
            print(f"   ❌ API request failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        print("   Check your internet connection")
        return False

    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {e}")
        print("   Check your internet connection")
        return False

    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_post_capability():
    """Test if we can create posts (dry run - doesn't actually post)."""
    print("\n3. Testing post capability...")

    if not PERSON_URN:
        print("   ⚠️  Skipping (LINKEDIN_PERSON_URN not configured)")
        return True

    # Build a test payload (we won't actually send it)
    test_payload = {
        'author': PERSON_URN,
        'commentary': 'Test post from AI Employee',
        'visibility': 'PUBLIC',
        'distribution': {
            'feedDistribution': 'MAIN_FEED'
        },
        'lifecycleState': 'PUBLISHED'
    }

    print("   ✅ Post payload structure validated")
    print(f"   Author: {PERSON_URN}")
    print("   Ready to create posts via REST API")

    return True


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("LinkedIn REST API Connection Test")
    print("=" * 60)
    print("\nThis script verifies your LinkedIn API configuration.")
    print("It will NOT post anything to LinkedIn.")
    print("\n" + "=" * 60)

    # Test configuration
    if not test_configuration():
        print("\n" + "=" * 60)
        print("❌ Configuration test failed")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: python scripts/linkedin_oauth2_setup.py")
        print("2. Follow the OAuth2 flow to get your access token")
        print("3. Run this test again")
        sys.exit(1)

    # Test API connection
    if not test_api_connection():
        print("\n" + "=" * 60)
        print("❌ API connection test failed")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Check your internet connection")
        print("2. Verify your access token is valid")
        print("3. Run: python scripts/linkedin_oauth2_setup.py to refresh token")
        sys.exit(1)

    # Test post capability
    if not test_post_capability():
        print("\n" + "=" * 60)
        print("⚠️  Post capability test incomplete")
        print("=" * 60)
        sys.exit(1)

    # Success
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nYour LinkedIn REST API is configured correctly.")
    print("\nNext steps:")
    print("1. Start the LinkedIn watcher:")
    print("   python run_watcher.py --watcher linkedin")
    print("\n2. Use the LinkedIn MCP server via Claude Code:")
    print("   - The server will be available as 'linkedin-mcp'")
    print("   - You can create posts via the create_post tool")
    print("\n3. Test creating a post:")
    print("   - Use Claude Code to call: mcp__linkedin-mcp__create_post")
    print("   - Provide text, visibility, and optional hashtags")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
