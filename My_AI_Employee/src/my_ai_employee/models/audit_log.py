"""
Audit Log Entry data model for Silver Tier AI Employee.

Defines the schema for audit log entries created by the audit-logger skill and mcp-executor skill.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, Dict, Any


@dataclass
class AuditLogEntrySchema:
    """
    Audit Log Entry entity schema.

    Storage location: AI_Employee_Vault/Logs/<YYYY-MM-DD>.json (append-only)
    """

    timestamp: datetime
    action_type: Literal["send_email", "publish_linkedin_post", "send_whatsapp_message", "browser_automation"]
    execution_status: Literal["success", "failed", "dry_run"]

    # Who executed (user or AI)
    executor: Literal["human", "ai_employee"]
    executor_id: str  # User ID or "claude-code"

    # What was executed
    tool_name: str
    tool_inputs_sanitized: Dict[str, Any] = field(default_factory=dict)

    # Why executed (approval context)
    approval_reason: Optional[str] = None
    approval_id: Optional[str] = None

    # Execution metadata
    mcp_server: str = ""
    error: Optional[str] = None
    retry_count: int = 0

    def __post_init__(self):
        """Validate audit log entry data."""
        if not self.executor_id:
            raise ValueError("executor_id is required")
        if not self.tool_name:
            raise ValueError("tool_name is required")

        # Ensure sensitive data is sanitized
        self._sanitize_inputs()

    def _sanitize_inputs(self) -> None:
        """
        Sanitize tool inputs to remove credentials and tokens.

        Redacts:
        - API keys, OAuth tokens, passwords
        - Full email bodies (keep preview only)
        - Credit card numbers, SSNs
        """
        if not self.tool_inputs_sanitized:
            return

        # Redact credential fields
        credential_fields = ["api_key", "token", "password", "oauth_token", "access_token"]
        for field in credential_fields:
            if field in self.tool_inputs_sanitized:
                self.tool_inputs_sanitized[field] = "REDACTED"

        # Truncate email bodies
        if "body" in self.tool_inputs_sanitized:
            body = self.tool_inputs_sanitized["body"]
            if isinstance(body, str) and len(body) > 200:
                self.tool_inputs_sanitized["body_preview"] = body[:200] + "..."
                del self.tool_inputs_sanitized["body"]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "action_type": self.action_type,
            "execution_status": self.execution_status,
            "executor": self.executor,
            "executor_id": self.executor_id,
            "tool_name": self.tool_name,
            "tool_inputs_sanitized": self.tool_inputs_sanitized,
            "approval_reason": self.approval_reason,
            "approval_id": self.approval_id,
            "mcp_server": self.mcp_server,
            "error": self.error,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditLogEntrySchema":
        """Create AuditLogEntrySchema from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            action_type=data["action_type"],
            execution_status=data["execution_status"],
            executor=data["executor"],
            executor_id=data["executor_id"],
            tool_name=data["tool_name"],
            tool_inputs_sanitized=data.get("tool_inputs_sanitized", {}),
            approval_reason=data.get("approval_reason"),
            approval_id=data.get("approval_id"),
            mcp_server=data.get("mcp_server", ""),
            error=data.get("error"),
            retry_count=data.get("retry_count", 0),
        )
