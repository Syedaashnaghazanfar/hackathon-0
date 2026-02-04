#!/usr/bin/env python3
"""Simple OAuth setup that prints the URL for manual authorization."""

import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
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
print("Gmail OAuth Setup - Manual Authorization")
print("=" * 70)
print()

if not Path(credentials_file).exists():
    print(f"❌ Error: {credentials_file} not found")
    exit(1)

print(f"✅ Found credentials file: {credentials_file}")
print()

# Create flow
flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes=scopes)

# Get authorization URL
auth_url, _ = flow.authorization_url(prompt='consent')

print("📋 AUTHORIZATION INSTRUCTIONS:")
print("=" * 70)
print()
print("1. Copy the URL below and paste it into your browser:")
print()
print(auth_url)
print()
print("2. Sign in with your Gmail account (user@gmail.com)")
print("3. Grant the requested permissions")
print("4. You'll be redirected to a URL like: http://localhost:8080/?code=...")
print("5. Copy the ENTIRE redirected URL and paste it below")
print()
print("=" * 70)
print()

# Wait for user to paste the redirect URL
redirect_url = input("Paste the redirect URL here: ").strip()

try:
    # Extract code from redirect URL
    flow.fetch_token(authorization_response=redirect_url)

    # Save credentials
    creds = flow.credentials
    with open(token_file, 'w') as f:
        f.write(creds.to_json())

    print()
    print("=" * 70)
    print("✅ SUCCESS! OAuth token saved to:", token_file)
    print("=" * 70)
    print()
    print("You can now run the Gmail watcher:")
    print("  uv run python watchers/gmail_watcher.py")
    print()

except Exception as e:
    print()
    print(f"❌ Error: {e}")
    print()
    print("Make sure you:")
    print("1. Added your email as a test user in Google Cloud Console")
    print("2. Copied the ENTIRE redirect URL (including http://localhost:8080/?code=...)")
    exit(1)
