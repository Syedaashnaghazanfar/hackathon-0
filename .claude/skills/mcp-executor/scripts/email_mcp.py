#!/usr/bin/env python3
"""
Email MCP Server - Send emails via Gmail API or SMTP.

Supports two backends:
1. Gmail API (OAuth 2.0) - Secure, requires Google account
2. SMTP (TLS) - Universal, works with any email provider

Backend selected via EMAIL_BACKEND environment variable:
- EMAIL_BACKEND=gmail (default) - Uses Gmail API
- EMAIL_BACKEND=smtp - Uses SMTP server

Type-safe with Pydantic v2 models for validation.
"""

import os
import smtplib
import base64
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="email-mcp")


# ============================================================================
# PYDANTIC MODELS - Type-safe email validation
# ============================================================================

class EmailRequest(BaseModel):
    """Email request model with validation."""

    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body (HTML or plain text)")
    cc: str = Field(default="", description="Comma-separated CC addresses (optional)")
    bcc: str = Field(default="", description="Comma-separated BCC addresses (optional)")

    @field_validator('to')
    @classmethod
    def validate_email(cls, v):
        """Validate email format."""
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email address')
        return v

    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v):
        """Subject cannot be empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Subject cannot be empty')
        return v

    @field_validator('body')
    @classmethod
    def validate_body(cls, v):
        """Body cannot be empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Body cannot be empty')
        return v


class EmailResponse(BaseModel):
    """Email response model."""

    success: bool = Field(..., description="Whether email was sent successfully")
    message_id: str = Field(default="", description="Message ID from email server")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    backend_used: str = Field(..., description="Backend used: 'gmail' or 'smtp'")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# ============================================================================
# EMAIL BACKEND ABSTRACT CLASS
# ============================================================================

class EmailBackend(ABC):
    """Abstract base class for email backends."""

    @abstractmethod
    def send(self, request: EmailRequest) -> EmailResponse:
        """Send email and return response."""
        pass

    @abstractmethod
    def validate_config(self) -> tuple[bool, str]:
        """Validate backend configuration. Returns (is_valid, error_message)."""
        pass


# ============================================================================
# GMAIL API BACKEND (OAuth 2.0)
# ============================================================================

class GmailBackend(EmailBackend):
    """
    Send emails via Gmail API with OAuth 2.0 authentication.

    Requires:
    - GMAIL_TOKEN_FILE: Path to token.json (from OAuth flow)
    - GMAIL_CREDENTIALS_FILE: Path to credentials.json (from Google Cloud)
    """

    def __init__(self):
        """Initialize Gmail backend."""
        self.token_file = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
        self.credentials_file = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Gmail API service."""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.exceptions import RefreshError
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/gmail.send']

            creds = None

            # Load existing credentials
            if Path(self.token_file).exists():
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)

            # If no valid credentials, perform OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except RefreshError as e:
                        logger.warning(f"Token refresh failed: {e}. Perform new OAuth flow.")
                        creds = None

                if not creds:
                    if not Path(self.credentials_file).exists():
                        raise FileNotFoundError(
                            f"credentials.json not found. "
                            f"Download from Google Cloud Console and place at {self.credentials_file}"
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save credentials for next use
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())

            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API service initialized successfully")

        except ImportError as e:
            raise ImportError(
                f"Gmail API libraries not installed. Install with: "
                f"pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            ) from e
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service: {e}")
            raise

    def send(self, request: EmailRequest) -> EmailResponse:
        """Send email via Gmail API."""
        try:
            if not self.service:
                raise RuntimeError("Gmail service not initialized")

            # Build MIME message
            message = MIMEMultipart('alternative')
            message['to'] = request.to
            message['subject'] = request.subject

            if request.cc:
                message['cc'] = request.cc

            # Attach body
            message.attach(MIMEText(request.body, 'html'))

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send via Gmail API
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"Email sent successfully via Gmail API. Message ID: {send_message['id']}")

            return EmailResponse(
                success=True,
                message_id=send_message['id'],
                timestamp=datetime.utcnow().isoformat() + 'Z',
                backend_used='gmail'
            )

        except Exception as e:
            error_msg = f"Gmail API error: {str(e)}"
            logger.error(error_msg)
            return EmailResponse(
                success=False,
                message_id="",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                backend_used='gmail',
                error=error_msg
            )

    def validate_config(self) -> tuple[bool, str]:
        """Validate Gmail configuration."""
        if not Path(self.credentials_file).exists():
            return False, f"credentials.json not found at {self.credentials_file}"
        return True, ""


# ============================================================================
# SMTP BACKEND (TLS - Universal)
# ============================================================================

class SMTPBackend(EmailBackend):
    """
    Send emails via SMTP with TLS encryption.

    Works with any email provider: Gmail, Outlook, custom servers, etc.

    Requires:
    - SMTP_HOST: SMTP server hostname
    - SMTP_PORT: SMTP port (typically 587 for TLS)
    - SMTP_USERNAME: Email address for authentication
    - SMTP_PASSWORD: Email password or app-specific password
    """

    def __init__(self):
        """Initialize SMTP backend."""
        self.host = os.getenv('SMTP_HOST', '')
        self.port = int(os.getenv('SMTP_PORT', '587'))
        self.username = os.getenv('SMTP_USERNAME', '')
        self.password = os.getenv('SMTP_PASSWORD', '')
        self.from_address = os.getenv('SMTP_FROM_ADDRESS', self.username)

    def send(self, request: EmailRequest) -> EmailResponse:
        """Send email via SMTP."""
        try:
            # Create MIME message
            message = MIMEMultipart('alternative')
            message['From'] = self.from_address
            message['To'] = request.to
            message['Subject'] = request.subject

            if request.cc:
                message['Cc'] = request.cc

            # Attach body
            message.attach(MIMEText(request.body, 'html'))

            # Connect to SMTP server with TLS
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                server.starttls()  # Encrypt connection
                server.login(self.username, self.password)

                # Send email (handle CC/BCC recipients)
                recipients = [request.to]
                if request.cc:
                    recipients.extend([addr.strip() for addr in request.cc.split(',')])
                if request.bcc:
                    recipients.extend([addr.strip() for addr in request.bcc.split(',')])

                server.sendmail(self.from_address, recipients, message.as_string())

            message_id = f"smtp-{datetime.utcnow().isoformat()}"
            logger.info(f"Email sent successfully via SMTP. Message ID: {message_id}")

            return EmailResponse(
                success=True,
                message_id=message_id,
                timestamp=datetime.utcnow().isoformat() + 'Z',
                backend_used='smtp'
            )

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD."
            logger.error(error_msg)
            return EmailResponse(
                success=False,
                message_id="",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                backend_used='smtp',
                error=error_msg
            )
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return EmailResponse(
                success=False,
                message_id="",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                backend_used='smtp',
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return EmailResponse(
                success=False,
                message_id="",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                backend_used='smtp',
                error=error_msg
            )

    def validate_config(self) -> tuple[bool, str]:
        """Validate SMTP configuration."""
        if not self.host:
            return False, "SMTP_HOST not configured"
        if not self.username:
            return False, "SMTP_USERNAME not configured"
        if not self.password:
            return False, "SMTP_PASSWORD not configured"
        return True, ""


# ============================================================================
# BACKEND FACTORY
# ============================================================================

def get_email_backend() -> EmailBackend:
    """
    Factory function to get the configured email backend.

    Returns:
        EmailBackend: Gmail or SMTP backend based on EMAIL_BACKEND env var

    Raises:
        RuntimeError: If backend is not properly configured
    """
    backend_name = os.getenv('EMAIL_BACKEND', 'gmail').lower()

    if backend_name == 'gmail':
        backend = GmailBackend()
        is_valid, error = backend.validate_config()
        if not is_valid:
            raise RuntimeError(f"Gmail backend configuration error: {error}")
        return backend

    elif backend_name == 'smtp':
        backend = SMTPBackend()
        is_valid, error = backend.validate_config()
        if not is_valid:
            raise RuntimeError(f"SMTP backend configuration error: {error}")
        return backend

    else:
        raise ValueError(
            f"Unknown EMAIL_BACKEND: {backend_name}. "
            f"Set to 'gmail' or 'smtp' in .env file."
        )


# ============================================================================
# MCP TOOLS - FastMCP exposed functions
# ============================================================================

@mcp.tool
def send_email(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = ""
) -> dict:
    """
    Send email via configured backend (Gmail API or SMTP).

    Automatically selects backend based on EMAIL_BACKEND environment variable:
    - EMAIL_BACKEND=gmail (default): Uses Gmail API with OAuth 2.0
    - EMAIL_BACKEND=smtp: Uses SMTP with TLS encryption

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body (plain text or HTML)
        cc: Comma-separated CC addresses (optional)
        bcc: Comma-separated BCC addresses (optional)

    Returns:
        {
            'success': True/False,
            'message_id': 'Unique message ID',
            'timestamp': 'ISO 8601 timestamp',
            'backend_used': 'gmail' or 'smtp',
            'error': 'Error message if failed (None if successful)'
        }

    Raises:
        ValueError: If email address is invalid
        RuntimeError: If backend is not properly configured
    """
    try:
        # Validate request with Pydantic
        request = EmailRequest(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc
        )

        # Get configured backend and send
        backend = get_email_backend()
        response = backend.send(request)

        # Convert Pydantic model to dict
        return response.model_dump()

    except ValueError as e:
        # Validation error
        return {
            'success': False,
            'message_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'backend_used': 'unknown',
            'error': f"Validation error: {str(e)}"
        }
    except Exception as e:
        # Configuration or unexpected error
        return {
            'success': False,
            'message_id': '',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'backend_used': 'unknown',
            'error': f"Error: {str(e)}"
        }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting Email MCP Server")
    logger.info(f"Backend: {os.getenv('EMAIL_BACKEND', 'gmail')}")
    mcp.run()
