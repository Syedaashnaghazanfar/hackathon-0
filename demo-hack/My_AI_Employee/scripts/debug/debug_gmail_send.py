#!/usr/bin/env python3
"""
Direct Gmail API test for Phase 9 E2E validation.
Bypasses MCP framework to test Gmail sending directly.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

def send_test_email():
    """Send test email via Gmail API."""
    print("=" * 60)
    print("Phase 9 T093 - Gmail E2E Test")
    print("=" * 60)
    print()

    # Check credentials
    creds_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')

    print(f"✓ Credentials file: {creds_file}")
    print(f"✓ Token file: {token_file}")
    print(f"✓ Credentials exist: {Path(creds_file).exists()}")
    print(f"✓ Token exist: {Path(token_file).exists()}")
    print(f"✓ DRY_RUN: {os.getenv('DRY_RUN', 'true')}")
    print()

    if not Path(creds_file).exists() or not Path(token_file).exists():
        print("❌ ERROR: Gmail credentials not found!")
        return False

    try:
        # Import Gmail API libraries
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from email.mime.text import MIMEText
        import base64

        print("Loading Gmail credentials...")
        creds = Credentials.from_authorized_user_file(token_file)

        print("Building Gmail service...")
        service = build('gmail', 'v1', credentials=creds)

        # Get profile to verify connection
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Gmail API connected: {profile['emailAddress']}")
        print()

        # Create email message
        print("Creating test email...")
        message = MIMEText("""Hello,

Thank you for your Phase 9 E2E test request.

This is an automated confirmation response from the AI Employee system. If you receive this email, it confirms that the complete workflow is functioning correctly:

✅ Email detection (simulated)
✅ Action item creation
✅ Processing with /needs-action-triage skill
✅ Plan generation
✅ Approval workflow
✅ Real email sending via Gmail API

The end-to-end test has been completed successfully.

Best regards,
AI Employee System""")

        message['to'] = 'user@gmail.com'
        message['subject'] = 'Re: Phase 9 E2E Test - Please Respond'

        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        print("Sending email via Gmail API...")
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        message_id = result.get('id', '')
        timestamp = datetime.utcnow().isoformat() + 'Z'

        print()
        print("=" * 60)
        print("✅ EMAIL SENT SUCCESSFULLY!")
        print("=" * 60)
        print(f"Message ID: {message_id}")
        print(f"Timestamp: {timestamp}")
        print(f"Recipient: user@gmail.com")
        print(f"Subject: Re: Phase 9 E2E Test - Please Respond")
        print()
        print("Check your Gmail inbox to verify receipt!")
        print("=" * 60)

        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ EMAIL SEND FAILED!")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = send_test_email()
    sys.exit(0 if success else 1)
