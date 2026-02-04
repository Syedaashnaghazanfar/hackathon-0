"""
Email MCP server for Silver Tier AI Employee.

Implements FastMCP server with send_email tool using Gmail API.
"""

import os
import logging
from typing import Optional
from pathlib import Path

from fastmcp import FastMCP
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from my_ai_employee.utils.auth_helper import OAuth2Helper
from my_ai_employee.config import get_config


logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("email")


@mcp.tool()
def send_email(
    to: str,
    subject: str,
    body: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    attachments: Optional[list[str]] = None,
) -> dict:
    """
    Send email via Gmail API.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body (plain text)
        cc: Optional CC recipients (comma-separated)
        bcc: Optional BCC recipients (comma-separated)
        attachments: Optional list of file paths to attach

    Returns:
        Dictionary with status and message_id or error

    Example:
        >>> send_email(
        ...     to="user@example.com",
        ...     subject="Test Email",
        ...     body="Hello, this is a test email."
        ... )
        {'status': 'success', 'message_id': 'abc123xyz'}
    """
    config = get_config()

    # Check dry-run mode
    if config.dry_run:
        logger.info(f"DRY RUN: Would send email to {to} with subject '{subject}'")
        logger.info(f"DRY RUN: Body preview: {body[:100]}...")
        return {
            "status": "dry_run",
            "message": f"Dry-run mode: Email to {to} not actually sent",
            "to": to,
            "subject": subject,
            "body_preview": body[:100],
        }

    try:
        # Initialize OAuth2 helper and get credentials
        oauth_helper = OAuth2Helper(
            credentials_file=config.gmail_credentials_file,
            token_file=config.gmail_token_file,
        )
        credentials = oauth_helper.get_valid_credentials()

        # Build Gmail API service
        service = build("gmail", "v1", credentials=credentials)

        # Create email message
        message = MIMEMultipart() if attachments else MIMEText(body)

        message["To"] = to
        message["Subject"] = subject

        if cc:
            message["Cc"] = cc
        if bcc:
            message["Bcc"] = bcc

        # Add body if multipart
        if attachments:
            message.attach(MIMEText(body, "plain"))

        # TODO: Add attachment support (requires file reading and encoding)
        # For now, attachments are ignored

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        # Send message
        sent_message = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )

        message_id = sent_message.get("id")
        logger.info(f"Email sent successfully to {to}, message ID: {message_id}")

        return {
            "status": "success",
            "message_id": message_id,
            "to": to,
            "subject": subject,
        }

    except HttpError as e:
        error_code = e.resp.status
        error_message = str(e)

        # Handle specific error codes
        if error_code == 401:
            logger.error(f"Authentication failed: {error_message}")
            return {
                "status": "error",
                "error_type": "authentication_failed",
                "error_message": "Gmail OAuth token expired or invalid. Re-authenticate.",
            }
        elif error_code == 429:
            logger.error(f"Rate limit exceeded: {error_message}")
            return {
                "status": "error",
                "error_type": "rate_limit_exceeded",
                "error_message": "Gmail API rate limit exceeded. Retry later.",
                "retry_after_seconds": int(e.resp.get("Retry-After", 60)),
            }
        else:
            logger.error(f"Gmail API error: {error_message}")
            return {
                "status": "error",
                "error_type": "api_error",
                "error_message": error_message,
                "error_code": error_code,
            }

    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return {
            "status": "error",
            "error_type": "unknown_error",
            "error_message": str(e),
        }


@mcp.tool()
def get_email_status(message_id: str) -> dict:
    """
    Get status of sent email.

    Args:
        message_id: Gmail message ID

    Returns:
        Dictionary with message status

    Example:
        >>> get_email_status("abc123xyz")
        {'status': 'sent', 'message_id': 'abc123xyz', 'thread_id': 'thread123'}
    """
    config = get_config()

    try:
        # Initialize OAuth2 helper and get credentials
        oauth_helper = OAuth2Helper(
            credentials_file=config.gmail_credentials_file,
            token_file=config.gmail_token_file,
        )
        credentials = oauth_helper.get_valid_credentials()

        # Build Gmail API service
        service = build("gmail", "v1", credentials=credentials)

        # Get message details
        message = (
            service.users().messages().get(userId="me", id=message_id).execute()
        )

        return {
            "status": "sent",
            "message_id": message_id,
            "thread_id": message.get("threadId"),
            "labels": message.get("labelIds", []),
        }

    except HttpError as e:
        if e.resp.status == 404:
            return {
                "status": "not_found",
                "message_id": message_id,
                "error": "Message not found",
            }
        else:
            return {
                "status": "error",
                "message_id": message_id,
                "error": str(e),
            }

    except Exception as e:
        logger.error(f"Failed to get email status: {e}", exc_info=True)
        return {
            "status": "error",
            "message_id": message_id,
            "error": str(e),
        }


if __name__ == "__main__":
    # Run MCP server
    mcp.run()
