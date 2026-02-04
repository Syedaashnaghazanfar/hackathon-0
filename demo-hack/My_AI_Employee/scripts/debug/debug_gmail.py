#!/usr/bin/env python3
"""Debug Gmail watcher - detailed logging of message fetching."""

import sys
from pathlib import Path

sys.path.insert(0, '.')

from watchers.gmail_watcher import GmailWatcher
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Gmail Watcher Debug - Detailed Message Fetching")
print("=" * 70)
print()

try:
    # Initialize watcher
    print("1. Initializing Gmail watcher...")
    watcher = GmailWatcher(vault_path='AI_Employee_Vault', check_interval=60)
    print("   ✅ Gmail watcher initialized")
    print()

    # Check connection
    print("2. Testing Gmail connection...")
    service = watcher.service
    profile = service.users().getProfile(userId='me').execute()
    email = profile.get('emailAddress')
    print(f"   ✅ Connected to Gmail: {email}")
    print()

    # Manually fetch messages to see what's happening
    print("3. Fetching unread messages directly from API...")
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='is:unread',
        maxResults=10
    ).execute()

    messages = results.get('messages', [])
    print(f"   ✅ API returned {len(messages)} message(s)")
    print()

    if messages:
        print("4. Message IDs:")
        for i, msg in enumerate(messages[:5], 1):
            print(f"   {i}. ID: {msg['id']}")
        print()

        print("5. Fetching full details for first message...")
        first_msg = messages[0]
        msg_details = service.users().messages().get(
            userId='me',
            id=first_msg['id'],
            format='full'
        ).execute()

        headers = msg_details['payload'].get('headers', [])
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')

        print(f"   From: {sender}")
        print(f"   Subject: {subject}")
        print()

    # Now test the watcher's internal method
    print("6. Testing watcher._fetch_new_messages()...")
    fetched_messages = watcher._fetch_new_messages()
    print(f"   ✅ Watcher returned {len(fetched_messages)} message(s)")
    print()

    if fetched_messages:
        print("7. First fetched message details:")
        first = fetched_messages[0]
        print(f"   ID: {first.get('id', 'N/A')}")
        print(f"   Sender: {first.get('sender', 'N/A')}")
        print(f"   Subject: {first.get('subject', 'N/A')}")
        print(f"   Body length: {len(first.get('body', ''))} chars")
        print()

    # Test check_for_updates with deduplication
    print("8. Testing watcher.check_for_updates() (with deduplication)...")
    new_messages = watcher.check_for_updates()
    print(f"   ✅ After deduplication: {len(new_messages)} message(s)")
    print()

    # Check dedupe file
    dedupe_file = Path('My_AI_Employee/.gmail_dedupe.json')
    if dedupe_file.exists():
        import json
        with open(dedupe_file) as f:
            dedupe_data = json.load(f)
        print(f"9. Deduplication state:")
        print(f"   Processed IDs: {dedupe_data.get('count', 0)}")
        print(f"   Last updated: {dedupe_data.get('last_updated', 'N/A')}")
    else:
        print("9. No deduplication file found")

    print()
    print("=" * 70)
    print("Debug Complete!")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
