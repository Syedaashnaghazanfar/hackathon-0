#!/usr/bin/env python3
"""
Shared audit logging utility for Gold Tier AI Employee.

Provides secure logging with credential sanitization for compliance
with Silver Tier Constitution Principle IX (Security and Audit Logging).
"""

import logging
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import re

logger = logging.getLogger(__name__)


class AuditLogger:
    """Audit logger with credential sanitization."""

    # Patterns to redact
    CREDENTIAL_PATTERNS = [
        r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',  # Bearer tokens
        r'token["\']?\s*:\s*["\']?[A-Za-z0-9\-._~+/]+["\']?',  # Token headers
        r'api[_-]?key["\']?\s*:\s*["\']?[A-Za-z0-9\-._~+/]+["\']?',  # API keys
        r'password["\']?\s*:\s*["\']?[^\s"\']+',  # Passwords
        r'secret["\']?\s*:\s*["\']?[^\s"\']+',  # Secrets
        r'session[_-]?id["\']?\s*:\s*["\']?[A-Za-z0-9\-]+',  # Session IDs
        r'authorization["\']?\s*:\s*[A-Za-z0-9\-._~+/]+',  # Basic auth
        r'client[_-]?secret["\']?\s*:\s*["\']?[^\s"\']+',  # Client secrets
        r'refresh[_-]?token["\']?\s*:\s*["\']?[A-Za-z0-9\-._~+/]+',  # Refresh tokens
        r'access[_-]?token["\']?\s*:\s*["\']?[A-Za-z0-9\-._~+/]+',  # Access tokens
    ]

    # Redaction placeholder
    REDACTED = '<REDACTED>'

    def __init__(self, vault_path: str, log_dir: Optional[str] = None):
        """
        Initialize audit logger.

        Args:
            vault_path: Path to Obsidian vault root
            log_dir: Directory for audit logs (default: vault_path/Logs/)
        """
        self.vault_path = Path(vault_path)
        self.log_dir = Path(log_dir) if log_dir else self.vault_path / 'Logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize credentials from dictionary.

        Args:
            data: Dictionary potentially containing credentials

        Returns:
            Sanitized dictionary with credentials redacted
        """
        sanitized = json.loads(json.dumps(data))  # Deep copy

        def sanitize_value(value: Any) -> Any:
            """Recursively sanitize a value."""
            if isinstance(value, str):
                for pattern in self.CREDENTIAL_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        return self.REDACTED
                return value
            elif isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            else:
                return value

        return sanitize_value(sanitized)

    def log_execution(
        self,
        action_id: str,
        action_type: str,
        user: str,
        ai_agent: str,
        approval_reason: str,
        execution_status: str,
        mcp_server: str,
        tool_name: str,
        tool_inputs: Dict[str, Any],
        tool_output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        """
        Log an external action execution to daily audit log.

        Args:
            action_id: Unique identifier for this action
            action_type: Type of action (e.g., 'send_email', 'post_to_facebook')
            user: User who approved the action
            ai_agent: AI agent that executed the action
            approval_reason: Reason for approval
            execution_status: 'success' | 'failure' | 'pending'
            mcp_server: MCP server used for execution
            tool_name: Tool/function name invoked
            tool_inputs: Input parameters (will be sanitized)
            tool_output: Output from tool (will be sanitized)
            error: Error message if failed
            retry_count: Number of retry attempts
        """
        timestamp = datetime.now().isoformat() + 'Z'

        log_entry = {
            "timestamp": timestamp,
            "action_id": action_id,
            "action_type": action_type,
            "user": user,
            "ai_agent": ai_agent,
            "approval_reason": approval_reason,
            "execution_status": execution_status,
            "mcp_server": mcp_server,
            "tool_name": tool_name,
            "tool_inputs_sanitized": self.sanitize(tool_inputs),
            "tool_output_sanitized": self.sanitize(tool_output) if tool_output else None,
            "error": error,
            "retry_count": retry_count
        }

        # Write to daily log file
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = self.log_dir / f"{date_str}.json"

        # Read existing log entries for today
        entries = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    entries = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read existing log file {log_file}: {e}")
                entries = []

        # Append new entry
        entries.append(log_entry)

        # Write updated log
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2)

        logger.debug(f"Audit log entry written to {log_file}")


if __name__ == "__main__":
    # Test audit logger
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        audit = AuditLogger(tmpdir)

        # Test logging
        audit.log_execution(
            action_id="test_action_001",
            action_type="test_action",
            user="test_user",
            ai_agent="claude-code-sonnet-4.5",
            approval_reason="Testing audit logging",
            execution_status="success",
            mcp_server="test-mcp",
            tool_name="test_tool",
            tool_inputs={
                "message": "Hello, World!",
                "api_key": "secret_key_12345"  # Should be redacted
            },
            tool_output={
                "result": "Success",
                "token": "auth_token_abc123"  # Should be redacted
            },
            retry_count=0
        )

        print("Audit log test complete. Check log file for redacted credentials.")
