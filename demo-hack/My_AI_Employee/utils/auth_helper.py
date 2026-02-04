"""
OAuth 2.0 helper for Gmail API and other Google services.
Inspired by Context7 patterns for google-api-python-client and google-auth-oauthlib.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource


class OAuth2Helper:
    """Helper for OAuth2 authentication and token persistence."""

    def __init__(self, credentials_file: str, token_file: str, scopes: List[str]):
        """
        Initialize OAuth2 helper.

        Args:
            credentials_file: Path to client_secrets.json downloaded from Google Cloud Console
            token_file: Path to store/load token.json (persistent credentials)
            scopes: List of OAuth scopes required
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self.scopes = scopes
        self._creds: Credentials = None
        self.logger = logging.getLogger(__name__)

    def get_credentials(self) -> Credentials:
        """
        Get valid OAuth 2.0 credentials, refreshing if necessary.

        Returns:
            Valid Credentials object

        Raises:
            FileNotFoundError: If credentials.json not found
            Exception: If authentication fails
        """
        # Try to load existing token
        if self.token_file.exists():
            try:
                self._creds = Credentials.from_authorized_user_file(
                    str(self.token_file),
                    self.scopes
                )
                self.logger.info(f"Loaded credentials from {self.token_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load token file: {e}")
                self._creds = None

        # Refresh if expired
        if self._creds and self._creds.expired and self._creds.refresh_token:
            self.logger.info("Refreshing expired token...")
            try:
                self._creds.refresh(Request())
                self._save_token()
                self.logger.info("Token refreshed successfully")
            except Exception as e:
                self.logger.error(f"Failed to refresh token: {e}")
                self._creds = None

        # If no valid credentials, start OAuth flow
        if not self._creds or not self._creds.valid:
            if not self.credentials_file.exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_file}. "
                    "Download it from Google Cloud Console and save as credentials.json"
                )

            self.logger.info("Starting OAuth 2.0 flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file),
                self.scopes
            )
            self._creds = flow.run_local_server(port=0)
            self._save_token()
            self.logger.info("OAuth 2.0 flow completed successfully")

        return self._creds

    def _save_token(self):
        """Save credentials to token file."""
        try:
            # Ensure directory exists
            self.token_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.token_file, 'w') as f:
                f.write(self._creds.to_json())
            self.logger.info(f"Saved token to {self.token_file}")
        except Exception as e:
            self.logger.error(f"Failed to save token: {e}")

    def build_service(self, service_name: str, version: str) -> Resource:
        """
        Build a Google API service using authenticated credentials.

        Args:
            service_name: API service name (e.g., 'gmail', 'drive')
            version: API version (e.g., 'v1')

        Returns:
            Google API Resource object
        """
        creds = self.get_credentials()
        return build(service_name, version, credentials=creds)

    def invalidate(self):
        """Invalidate current credentials and delete token file."""
        self._creds = None
        if self.token_file.exists():
            try:
                self.token_file.unlink()
                self.logger.info(f"Deleted token file: {self.token_file}")
            except Exception as e:
                self.logger.error(f"Failed to delete token file: {e}")


def load_auth_from_env(
    credentials_env: str = "GMAIL_CREDENTIALS_FILE",
    token_env: str = "GMAIL_TOKEN_FILE",
    scopes_env: str = "GMAIL_SCOPES"
) -> Dict[str, Any]:
    """
    Load OAuth2 configuration from environment variables.

    Args:
        credentials_env: Environment variable name for credentials file path
        token_env: Environment variable name for token file path
        scopes_env: Environment variable name for comma-separated scopes

    Returns:
        Dictionary with 'credentials_file', 'token_file', 'scopes'
    """
    credentials_file = os.getenv(credentials_env, "credentials.json")
    token_file = os.getenv(token_env, "token.json")

    # Default scopes for Gmail
    default_scopes = [
        'https://www.googleapis.com/auth/gmail.modify',  # Read/write access
        'https://www.googleapis.com/auth/gmail.labels',   # Manage labels
        'https://www.googleapis.com/auth/gmail.settings.basic'  # Basic settings
    ]

    scopes_str = os.getenv(scopes_env)
    scopes = default_scopes
    if scopes_str:
        scopes = scopes_str.split(',')

    return {
        'credentials_file': credentials_file,
        'token_file': token_file,
        'scopes': scopes
    }
