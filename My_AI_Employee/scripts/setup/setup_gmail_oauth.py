#!/usr/bin/env python3
"""
Gmail OAuth2 setup script for Silver Tier AI Employee.

Runs interactive OAuth2 flow:
1. Opens browser for Google consent screen
2. User grants permissions
3. Saves credentials.json and token.json for future use
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from my_ai_employee.utils import OAuth2Helper


def main():
    """Run Gmail OAuth2 setup."""
    print("=" * 60)
    print("Gmail OAuth2 Setup for Silver Tier AI Employee")
    print("=" * 60)
    print()

    # Check for credentials.json
    credentials_file = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
    if not Path(credentials_file).exists():
        print(f"ERROR: {credentials_file} not found!")
        print()
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download JSON → Save as 'credentials.json' in project root")
        print()
        sys.exit(1)

    print(f"✓ Found credentials file: {credentials_file}")
    print()

    # Initialize OAuth2Helper
    try:
        oauth_helper = OAuth2Helper()
        print("Starting OAuth2 flow...")
        print("A browser window will open for Google consent screen.")
        print()

        # Load credentials (will trigger interactive flow if needed)
        credentials = oauth_helper.load_credentials()

        print()
        print("=" * 60)
        print("✓ OAuth2 setup complete!")
        print("=" * 60)
        print()
        print(f"Token saved to: {oauth_helper.token_file}")
        print()
        print("You can now use the Gmail watcher:")
        print("  uv run python -m my_ai_employee.watchers.gmail_watcher")
        print()

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: OAuth2 setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
