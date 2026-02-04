#!/usr/bin/env python3
"""Complete Gmail OAuth setup with authorization code."""

import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

# OAuth scopes
scopes = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic'
]

credentials_file = 'credentials.json'
token_file = 'token.json'

if len(sys.argv) < 2:
    print("Usage: python complete_oauth.py <authorization_code_or_url>")
    print()
    print("Example:")
    print("  python complete_oauth.py '4/0AanRRrtXXXXXXXXXXXXXXXX'")
    print("  OR")
    print("  python complete_oauth.py 'http://localhost/?code=4/0AanRRrt...'")
    sys.exit(1)

auth_input = sys.argv[1].strip()

# Extract code from URL if full URL was provided
if auth_input.startswith('http'):
    parsed = urlparse(auth_input)
    params = parse_qs(parsed.query)
    if 'code' in params:
        auth_code = params['code'][0]
    else:
        print("❌ Error: No 'code' parameter found in URL")
        sys.exit(1)
else:
    auth_code = auth_input

print("=" * 70)
print("Completing Gmail OAuth Setup...")
print("=" * 70)
print()

try:
    # Create flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file,
        scopes=scopes,
        redirect_uri='http://localhost'
    )

    # Exchange code for token
    print("Exchanging authorization code for access token...")
    flow.fetch_token(code=auth_code)

    # Save credentials
    creds = flow.credentials
    with open(token_file, 'w') as f:
        f.write(creds.to_json())

    print(f"✅ Token saved to: {token_file}")
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
    print("Next steps:")
    print("1. Run the Gmail watcher: uv run python watchers/gmail_watcher.py")
    print("2. Or use the multi-watcher orchestrator for all watchers")
    print()

except Exception as e:
    print()
    print(f"❌ Error: {e}")
    print()
    print("Troubleshooting:")
    print("1. Make sure you copied the correct authorization code")
    print("2. The code should start with '4/0A' or similar")
    print("3. Make sure you added your email as a test user in Google Cloud Console")
    print("4. Try generating a new authorization URL if the code expired")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
