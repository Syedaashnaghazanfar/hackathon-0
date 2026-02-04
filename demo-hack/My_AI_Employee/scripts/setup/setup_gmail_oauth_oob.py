#!/usr/bin/env python3
"""Gmail OAuth setup using out-of-band (OOB) flow for WSL compatibility."""

import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# OAuth scopes
scopes = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic'
]

credentials_file = 'credentials.json'
token_file = 'token.json'

print("=" * 70)
print("Gmail OAuth Setup - Out-of-Band Flow")
print("=" * 70)
print()

if not Path(credentials_file).exists():
    print(f"❌ Error: {credentials_file} not found")
    exit(1)

print(f"✅ Found credentials file: {credentials_file}")
print()

# Create flow with redirect to localhost (no specific port)
flow = InstalledAppFlow.from_client_secrets_file(
    credentials_file,
    scopes=scopes,
    redirect_uri='http://localhost'
)

# Get authorization URL
auth_url, _ = flow.authorization_url(
    prompt='consent',
    access_type='offline',
    include_granted_scopes='true'
)

print("📋 STEP 1: AUTHORIZE THE APPLICATION")
print("=" * 70)
print()
print("Copy this URL and open it in your browser:")
print()
print(auth_url)
print()
print("=" * 70)
print()
print("📋 STEP 2: COMPLETE AUTHORIZATION")
print()
print("1. Sign in with: user@gmail.com")
print("2. Click 'Continue' to grant permissions")
print("3. After authorization, you'll see an error page (this is normal!)")
print("4. Look at the URL in your browser address bar")
print("5. It will look like: http://localhost/?code=4/0AanRRrt...")
print("6. Copy ONLY the code part (everything after 'code=')")
print()
print("Example:")
print("  URL: http://localhost/?code=4/0AanRRrtXXXXXXXXXXXXXXXX&scope=...")
print("  Copy: 4/0AanRRrtXXXXXXXXXXXXXXXX")
print()
print("=" * 70)
print()

# Wait for user to paste the authorization code
auth_code = input("Paste the authorization code here: ").strip()

if not auth_code:
    print("❌ Error: No authorization code provided")
    exit(1)

try:
    # Exchange code for token
    flow.fetch_token(code=auth_code)

    # Save credentials
    creds = flow.credentials
    with open(token_file, 'w') as f:
        f.write(creds.to_json())

    print()
    print("=" * 70)
    print("✅ SUCCESS! OAuth token saved to:", token_file)
    print("=" * 70)
    print()

    # Test the connection
    print("Testing Gmail connection...")
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    email = profile.get('emailAddress')

    print(f"✅ Connected to Gmail: {email}")
    print()

    # Check for unread messages
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='is:unread',
        maxResults=5
    ).execute()

    messages = results.get('messages', [])
    print(f"✅ Found {len(messages)} unread message(s)")
    print()
    print("=" * 70)
    print("🎉 Setup Complete!")
    print("=" * 70)
    print()
    print("You can now run the Gmail watcher:")
    print("  uv run python watchers/gmail_watcher.py")
    print()

except Exception as e:
    print()
    print(f"❌ Error: {e}")
    print()
    print("Troubleshooting:")
    print("1. Make sure you copied ONLY the code (not the entire URL)")
    print("2. The code should start with '4/0A' or similar")
    print("3. Make sure you added your email as a test user in Google Cloud Console")
    print()
    import traceback
    traceback.print_exc()
    exit(1)
