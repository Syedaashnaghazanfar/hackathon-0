"""
OAuth2 authentication helper for Silver Tier AI Employee.

Provides OAuth2Helper class for Gmail token management with automatic refresh.
"""

import os
from pathlib import Path
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class OAuth2Helper:
    """
    OAuth2 helper for Gmail API authentication.

    Handles token loading, refreshing, and saving with automatic credential rotation.
    """

    def __init__(
        self,
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None,
        scopes: Optional[list[str]] = None,
    ):
        """
        Initialize OAuth2Helper.

        Args:
            credentials_file: Path to credentials.json (defaults to GMAIL_CREDENTIALS_FILE env var)
            token_file: Path to token.json (defaults to GMAIL_TOKEN_FILE env var)
            scopes: List of OAuth2 scopes (defaults to GMAIL_SCOPES env var)
        """
        self.credentials_file = credentials_file or os.getenv(
            "GMAIL_CREDENTIALS_FILE", "credentials.json"
        )
        self.token_file = token_file or os.getenv("GMAIL_TOKEN_FILE", "token.json")

        # Parse scopes from environment or use defaults
        if scopes is None:
            scopes_env = os.getenv("GMAIL_SCOPES", "https://www.googleapis.com/auth/gmail.modify")
            scopes = [scope.strip() for scope in scopes_env.split(",")]

        self.scopes = scopes
        self.credentials: Optional[Credentials] = None

    def load_credentials(self) -> Credentials:
        """
        Load OAuth2 credentials from token file or initiate interactive flow.

        Returns:
            Valid OAuth2 credentials

        Raises:
            FileNotFoundError: If credentials.json not found and no valid token exists
        """
        credentials = None

        # Load existing token
        if Path(self.token_file).exists():
            credentials = Credentials.from_authorized_user_file(self.token_file, self.scopes)

        # Refresh if expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            self._save_credentials(credentials)

        # Run interactive flow if no valid credentials
        if not credentials or not credentials.valid:
            if not Path(self.credentials_file).exists():
                raise FileNotFoundError(
                    f"Credentials file not found: {self.credentials_file}. "
                    "Please download OAuth2 credentials from Google Cloud Console."
                )

            flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
            credentials = flow.run_local_server(port=0)
            self._save_credentials(credentials)

        self.credentials = credentials
        return credentials

    def _save_credentials(self, credentials: Credentials) -> None:
        """
        Save credentials to token file.

        Args:
            credentials: OAuth2 credentials to save
        """
        with open(self.token_file, "w") as token:
            token.write(credentials.to_json())

    def get_valid_credentials(self) -> Credentials:
        """
        Get valid OAuth2 credentials (load and refresh if needed).

        Returns:
            Valid OAuth2 credentials

        Example:
            >>> helper = OAuth2Helper()
            >>> creds = helper.get_valid_credentials()
            >>> # Use creds for Gmail API calls
        """
        if self.credentials is None:
            return self.load_credentials()

        # Refresh if expired
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
            self._save_credentials(self.credentials)

        return self.credentials

    def revoke_credentials(self) -> None:
        """
        Revoke OAuth2 credentials and delete token file.

        Use this to force re-authentication on next run.
        """
        if self.credentials:
            self.credentials = None

        if Path(self.token_file).exists():
            Path(self.token_file).unlink()
