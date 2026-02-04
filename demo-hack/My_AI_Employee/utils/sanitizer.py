"""
Production-ready credential sanitization utility.
Inspired by @audit-logger skill logic.
"""

import re
from typing import Dict, Any, Union, List


class CredentialSanitizer:
    """Sanitize sensitive credentials using common patterns and field-name matching."""

    # Patterns to redact directly within strings
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'api_key': r'(?i)(api[_-]?key|apikey|access[_-]?token|token)["\']?\s*[=:]\s*["\']?[A-Za-z0-9\-_.~+/]+=*["\']?',
    }

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Partial redaction of email: a****@example.com"""
        if not email or '@' not in email:
            return email
        local, domain = email.split('@', 1)
        return f"{local[:1]}****@{domain}"

    @staticmethod
    def sanitize_token(token: str, visible_length: int = 4) -> str:
        """Partial redaction of token: abcd****"""
        if not token or len(token) <= visible_length:
            return "[REDACTED]"
        return f"{token[:visible_length]}****"

    @classmethod
    def sanitize_dict(cls, data: Any) -> Any:
        """Recursively sanitize dictionary or list objects."""
        if isinstance(data, list):
            return [cls.sanitize_dict(item) for item in data]

        if not isinstance(data, dict):
            return data

        sanitized = {}
        # Sensitivity triggers
        SENSITIVE_KEYS = {
            'password', 'token', 'api_key', 'secret', 'credential',
            'auth', 'bearer', 'access_token', 'refresh_token', 'credit_card', 'pan'
        }

        for key, value in data.items():
            key_lower = str(key).lower()

            if any(s in key_lower for s in SENSITIVE_KEYS):
                if isinstance(value, str):
                    if '@' in value and '.' in value:
                        sanitized[key] = cls.sanitize_email(value)
                    else:
                        sanitized[key] = cls.sanitize_token(value)
                else:
                    sanitized[key] = "[REDACTED]"
            elif isinstance(value, (dict, list)):
                sanitized[key] = cls.sanitize_dict(value)
            else:
                sanitized[key] = value

        return sanitized
