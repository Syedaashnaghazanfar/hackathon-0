#!/usr/bin/env python3
"""Test script for Gmail watcher - manual OAuth flow for WSL."""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

def main():
    """Test Gmail watcher with manual OAuth flow."""
    print("=" * 60)
    print("Gmail Watcher OAuth Setup (Manual Flow for WSL)")
    print("=" * 60)

    # Check credentials file
    credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    if not Path(credentials_file).exists():
        print(f"❌ Credentials file not found: {credentials_file}")
        return 1

    print(f"✅ Found credentials file: {credentials_file}")

    # Check if token already exists
    token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
    if Path(token_file).exists():
        print(f"\n⚠️  Token file already exists: {token_file}")
        response = input("Delete and re-authenticate? (y/n): ")
        if response.lower() == 'y':
            Path(token_file).unlink()
            print("✅ Deleted existing token")
        else:
            print("Using existing token...")
            try:
                creds = Credentials.from_authorized_user_file(token_file)
                service = build('gmail', 'v1', credentials=creds)
                profile = service.users().getProfile(userId='me').execute()
                print(f"✅ Already authenticated as: {profile.get('emailAddress')}")
                return 0
            except Exception as e:
                print(f"❌ Existing token is invalid: {e}")
                Path(token_file).unlink()
                print("Deleted invalid token, will re-authenticate...")

    # OAuth scopes
    scopes = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.labels',
        'https://www.googleapis.com/auth/gmail.settings.basic'
    ]

    print("\n" + "=" * 60)
    print("Starting OAuth 2.0 Flow (Manual)")
    print("=" * 60)

    # Create flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file,
        scopes=scopes
    )

    # Run manual flow - this will print the URL
    print("\n📋 INSTRUCTIONS:")
    print("1. A browser window will attempt to open")
    print("2. If it doesn't open, copy the URL below and paste it in your browser")
    print("3. Complete the Google authorization")
    print("4. The script will automatically continue after authorization")
    print()

    try:
        # This will try to open browser and print URL as fallback
        creds = flow.run_local_server(
            port=8080,
            authorization_prompt_message='Please visit this URL to authorize: {url}',
            success_message='Authorization successful! You can close this window.',
            open_browser=True
        )

        # Save token
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        print(f"\n✅ Token saved to: {token_file}")

        # Test connection
        print("\n" + "=" * 60)
        print("Testing Gmail Connection...")
        print("=" * 60)

        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress')
        print(f"✅ Successfully connected to Gmail: {email}")

        # Check for unread messages
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q='is:unread',
            maxResults=5
        ).execute()

        messages = results.get('messages', [])
        if messages:
            print(f"\n✅ Found {len(messages)} unread message(s)")
        else:
            print("\nℹ️  No unread messages found")

        print("\n" + "=" * 60)
        print("✅ Setup Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run the Gmail watcher: uv run python watchers/gmail_watcher.py")
        print("2. Send yourself a test email")
        print("3. Check AI_Employee_Vault/Needs_Action/ for new action items")
        print()

        return 0

    except Exception as e:
        print(f"\n❌ OAuth flow failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you added your email as a test user in Google Cloud Console")
        print("2. Check that your credentials.json is valid")
        print("3. Try running in a native terminal (not WSL) if browser won't open")
        return 1

if __name__ == '__main__':
    sys.exit(main())
