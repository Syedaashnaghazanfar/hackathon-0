#!/usr/bin/env python3
"""
LinkedIn OAuth2 Authentication Helper

This script helps you obtain LinkedIn OAuth2 access token for the REST API.
Run this once to authenticate and get your access token.

Usage:
    python linkedin_oauth2_setup.py
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OAuth2 Configuration
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8080/linkedin/callback')

# LinkedIn OAuth2 endpoints
AUTH_URL = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
USERINFO_URL = 'https://api.linkedin.com/v2/userinfo'

# Required scopes
SCOPES = ['openid', 'profile', 'email', 'w_member_social']

# Global variable to store authorization code
authorization_code = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP server handler to receive OAuth2 callback."""

    def do_GET(self):
        """Handle GET request from OAuth2 callback."""
        global authorization_code

        # Parse query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            authorization_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        elif 'error' in params:
            error = params['error'][0]
            error_description = params.get('error_description', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>Error: {error}</p>
                    <p>Description: {error_description}</p>
                </body>
                </html>
            """.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Invalid Callback</h1>
                    <p>No authorization code received.</p>
                </body>
                </html>
            """)

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def check_environment():
    """Check if required environment variables are set."""
    if not CLIENT_ID:
        print("❌ Error: LINKEDIN_CLIENT_ID not found in .env")
        print("\nPlease add to your .env file:")
        print("LINKEDIN_CLIENT_ID=your_client_id_here")
        return False

    if not CLIENT_SECRET:
        print("❌ Error: LINKEDIN_CLIENT_SECRET not found in .env")
        print("\nPlease add to your .env file:")
        print("LINKEDIN_CLIENT_SECRET=your_client_secret_here")
        return False

    return True


def get_authorization_code():
    """Open browser for user authorization and get authorization code."""
    global authorization_code

    # Build authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }
    auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"

    print("\n" + "=" * 60)
    print("LinkedIn OAuth2 Authentication")
    print("=" * 60)
    print("\n1. Opening browser for LinkedIn authorization...")
    print(f"   If browser doesn't open, visit: {auth_url}\n")

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    print("2. Waiting for authorization callback...")
    print(f"   Listening on {REDIRECT_URI}\n")

    # Extract port from redirect URI
    port = int(urlparse(REDIRECT_URI).port or 8080)

    # Start HTTP server
    server = HTTPServer(('localhost', port), CallbackHandler)
    server.handle_request()  # Handle one request then stop

    if not authorization_code:
        print("❌ Failed to receive authorization code")
        return None

    print("✅ Authorization code received")
    return authorization_code


def exchange_code_for_token(code):
    """Exchange authorization code for access token."""
    print("\n3. Exchanging authorization code for access token...")

    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    try:
        response = requests.post(TOKEN_URL, data=token_data, timeout=30)
        response.raise_for_status()

        token_info = response.json()
        print("✅ Access token obtained")

        return token_info

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get access token: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None


def get_user_info(access_token):
    """Get user information to retrieve person URN."""
    print("\n4. Fetching user information...")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    try:
        response = requests.get(USERINFO_URL, headers=headers, timeout=30)
        response.raise_for_status()

        user_info = response.json()
        print("✅ User information retrieved")

        return user_info

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get user info: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None


def save_credentials(token_info, user_info):
    """Save credentials to .env file."""
    print("\n5. Saving credentials...")

    access_token = token_info.get('access_token')
    expires_in = token_info.get('expires_in', 'Unknown')
    person_urn = f"urn:li:person:{user_info.get('sub')}"

    # Read current .env file
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        env_content = ""

    # Update or add LinkedIn credentials
    lines = env_content.split('\n')
    updated_lines = []
    found_token = False
    found_urn = False

    for line in lines:
        if line.startswith('LINKEDIN_ACCESS_TOKEN='):
            updated_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}')
            found_token = True
        elif line.startswith('LINKEDIN_PERSON_URN='):
            updated_lines.append(f'LINKEDIN_PERSON_URN={person_urn}')
            found_urn = True
        else:
            updated_lines.append(line)

    # Add if not found
    if not found_token:
        updated_lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}')
    if not found_urn:
        updated_lines.append(f'LINKEDIN_PERSON_URN={person_urn}')

    # Write back to .env
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_lines))

    print("✅ Credentials saved to .env")
    print("\n" + "=" * 60)
    print("LinkedIn OAuth2 Setup Complete!")
    print("=" * 60)
    print(f"\n✅ Access Token: {access_token[:20]}...")
    print(f"✅ Person URN: {person_urn}")
    print(f"✅ Expires in: {expires_in} seconds (~{expires_in // 3600} hours)")
    print("\n⚠️  Note: Access tokens expire. You'll need to re-run this script")
    print("   when the token expires (typically 60 days).")
    print("\n" + "=" * 60)


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("LinkedIn OAuth2 Authentication Setup")
    print("=" * 60)
    print("\nThis script will help you obtain LinkedIn API credentials.")
    print("\nPrerequisites:")
    print("1. LinkedIn Developer App created at https://www.linkedin.com/developers/")
    print("2. LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in .env")
    print(f"3. Redirect URI configured: {REDIRECT_URI}")
    print("\n" + "=" * 60)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Get authorization code
    code = get_authorization_code()
    if not code:
        sys.exit(1)

    # Exchange for token
    token_info = exchange_code_for_token(code)
    if not token_info:
        sys.exit(1)

    # Get user info
    user_info = get_user_info(token_info['access_token'])
    if not user_info:
        sys.exit(1)

    # Save credentials
    save_credentials(token_info, user_info)

    print("\n✅ Setup complete! You can now use the LinkedIn REST API.")
    print("\nNext steps:")
    print("1. Test the connection: python test_linkedin_api.py")
    print("2. Start the LinkedIn watcher: python run_watcher.py --watcher linkedin")
    print("3. Use the LinkedIn MCP server via Claude Code")


if __name__ == '__main__':
    main()
