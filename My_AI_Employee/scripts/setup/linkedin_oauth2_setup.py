#!/usr/bin/env python3
"""
LinkedIn OAuth2 setup script for Silver Tier AI Employee.

Runs interactive OAuth2 flow:
1. Opens browser for LinkedIn authorization
2. User grants permissions
3. Exchanges authorization code for access token
4. Saves LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN to .env
"""

import os
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlencode, parse_qs, urlparse

import requests


def main():
    """Run LinkedIn OAuth2 setup."""
    print("=" * 60)
    print("LinkedIn OAuth2 Setup for Silver Tier AI Employee")
    print("=" * 60)
    print()

    # Get client credentials from user
    print("Before continuing, you need:")
    print("1. LinkedIn Developer App created at https://www.linkedin.com/developers/apps")
    print("2. 'Share on LinkedIn' product access granted")
    print("3. Client ID and Client Secret from the app")
    print()

    client_id = input("Enter LinkedIn Client ID: ").strip()
    if not client_id:
        print("ERROR: Client ID is required")
        sys.exit(1)

    client_secret = input("Enter LinkedIn Client Secret: ").strip()
    if not client_secret:
        print("ERROR: Client Secret is required")
        sys.exit(1)

    # OAuth2 parameters
    redirect_uri = "http://localhost:8080/callback"
    scope = "w_member_social"  # Permission to post on behalf of user

    # Step 1: Build authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"

    print()
    print("=" * 60)
    print("Step 1: Authorize Application")
    print("=" * 60)
    print()
    print("Opening browser for LinkedIn authorization...")
    print(f"URL: {auth_url}")
    print()
    print("After authorizing:")
    print("1. You'll be redirected to a URL starting with http://localhost:8080/callback")
    print("2. Copy the ENTIRE URL from your browser address bar")
    print("3. Paste it below")
    print()

    # Open browser
    webbrowser.open(auth_url)

    # Wait for user to paste callback URL
    callback_url = input("Paste the callback URL here: ").strip()

    # Extract authorization code
    try:
        parsed = urlparse(callback_url)
        query_params = parse_qs(parsed.query)
        auth_code = query_params.get("code", [None])[0]

        if not auth_code:
            print("ERROR: No authorization code found in URL")
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: Failed to parse callback URL: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("Step 2: Exchange Code for Access Token")
    print("=" * 60)
    print()

    # Step 2: Exchange code for access token
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_response = response.json()

        access_token = token_response.get("access_token")
        if not access_token:
            print("ERROR: No access token in response")
            print(f"Response: {token_response}")
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: Failed to exchange code for token: {e}")
        sys.exit(1)

    print("✓ Access token received")
    print()

    # Step 3: Get user profile to extract Person URN
    print("=" * 60)
    print("Step 3: Fetch User Profile")
    print("=" * 60)
    print()

    profile_url = "https://api.linkedin.com/v2/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()
        profile = response.json()

        person_id = profile.get("id")
        if not person_id:
            print("ERROR: No person ID in profile response")
            print(f"Response: {profile}")
            sys.exit(1)

        person_urn = f"urn:li:person:{person_id}"

    except Exception as e:
        print(f"ERROR: Failed to fetch user profile: {e}")
        sys.exit(1)

    print(f"✓ Person URN: {person_urn}")
    print()

    # Step 4: Update .env file
    print("=" * 60)
    print("Step 4: Update .env File")
    print("=" * 60)
    print()

    env_file = Path(".env")
    env_lines = []

    # Read existing .env if it exists
    if env_file.exists():
        with open(env_file, "r") as f:
            env_lines = f.readlines()

    # Update or add LinkedIn credentials
    updated_access_token = False
    updated_person_urn = False

    for i, line in enumerate(env_lines):
        if line.startswith("LINKEDIN_ACCESS_TOKEN="):
            env_lines[i] = f"LINKEDIN_ACCESS_TOKEN={access_token}\n"
            updated_access_token = True
        elif line.startswith("LINKEDIN_PERSON_URN="):
            env_lines[i] = f"LINKEDIN_PERSON_URN={person_urn}\n"
            updated_person_urn = True

    # Append if not found
    if not updated_access_token:
        env_lines.append(f"LINKEDIN_ACCESS_TOKEN={access_token}\n")
    if not updated_person_urn:
        env_lines.append(f"LINKEDIN_PERSON_URN={person_urn}\n")

    # Write back to .env
    with open(env_file, "w") as f:
        f.writelines(env_lines)

    print(f"✓ Updated {env_file}")
    print()
    print("=" * 60)
    print("✓ LinkedIn OAuth2 setup complete!")
    print("=" * 60)
    print()
    print("You can now use the LinkedIn watcher:")
    print("  uv run python -m my_ai_employee.watchers.linkedin_watcher")
    print()
    print("IMPORTANT: Access tokens expire after 60 days.")
    print("Re-run this script when the token expires.")
    print()


if __name__ == "__main__":
    main()
