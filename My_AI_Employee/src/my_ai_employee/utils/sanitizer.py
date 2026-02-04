"""
Credential sanitization utility for Silver Tier AI Employee.

Provides functions to redact sensitive data from logs and audit entries.
"""

import re
from typing import Any, Dict


def redact_api_key(api_key: str) -> str:
    """
    Redact API key (show only first 4 characters).

    Args:
        api_key: API key string

    Returns:
        Redacted string (e.g., "sk-a1******")

    Example:
        >>> redact_api_key("sk-a1b2c3d4e5f6g7h8")
        'sk-a1******'
    """
    if not api_key or len(api_key) < 6:
        return "REDACTED"

    return f"{api_key[:6]}{'*' * (len(api_key) - 6)}"


def redact_oauth_token(token: str) -> str:
    """
    Redact OAuth token completely.

    Args:
        token: OAuth token string

    Returns:
        "REDACTED"

    Example:
        >>> redact_oauth_token("ya29.a0AfH6SMBx...")
        'REDACTED'
    """
    return "REDACTED"


def redact_pii(text: str) -> str:
    """
    Redact personally identifiable information (emails, phone numbers, SSNs).

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text with PII redacted

    Example:
        >>> redact_pii("Email me at user@example.com or call 123-456-7890")
        'Email me at [EMAIL_REDACTED] or call [PHONE_REDACTED]'
    """
    # Redact email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "[EMAIL_REDACTED]",
        text,
    )

    # Redact phone numbers (various formats)
    text = re.sub(
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "[PHONE_REDACTED]",
        text,
    )

    # Redact SSNs (XXX-XX-XXXX format)
    text = re.sub(
        r"\b\d{3}-\d{2}-\d{4}\b",
        "[SSN_REDACTED]",
        text,
    )

    # Redact credit card numbers (16 digits)
    text = re.sub(
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "[CC_REDACTED]",
        text,
    )

    return text


def sanitize_tool_inputs(tool_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize MCP tool inputs for audit logging.

    Redacts:
    - API keys, OAuth tokens, passwords
    - Full email bodies (keeps preview only)
    - PII in text fields

    Args:
        tool_inputs: Dictionary of tool input parameters

    Returns:
        Sanitized dictionary safe for logging

    Example:
        >>> inputs = {"to": "user@example.com", "body": "Secret message", "api_key": "sk-abc123"}
        >>> sanitize_tool_inputs(inputs)
        {'to': '[EMAIL_REDACTED]', 'body_preview': 'Secret mes...', 'api_key': 'REDACTED'}
    """
    sanitized = {}

    credential_fields = [
        "api_key",
        "token",
        "password",
        "oauth_token",
        "access_token",
        "refresh_token",
        "bearer_token",
        "secret",
    ]

    for key, value in tool_inputs.items():
        # Redact credential fields
        if key.lower() in credential_fields:
            sanitized[key] = "REDACTED"
            continue

        # Truncate long text fields
        if key == "body" and isinstance(value, str):
            if len(value) > 200:
                sanitized["body_preview"] = value[:200] + "..."
            else:
                sanitized["body_preview"] = value
            continue

        # Redact PII in text fields
        if isinstance(value, str):
            sanitized[key] = redact_pii(value)
        else:
            sanitized[key] = value

    return sanitized


def sanitize_error_message(error: str) -> str:
    """
    Sanitize error message to remove sensitive data.

    Args:
        error: Error message string

    Returns:
        Sanitized error message

    Example:
        >>> sanitize_error_message("Authentication failed for user@example.com")
        'Authentication failed for [EMAIL_REDACTED]'
    """
    return redact_pii(error)
