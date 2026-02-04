"""
Execution Plan data model for Silver Tier AI Employee.

Defines the schema for execution plans created by the triage skill and executed by the
mcp-executor skill.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, Dict, Any, List


@dataclass
class ExecutionPlanSchema:
    """
    Execution Plan entity schema.

    Storage location: AI_Employee_Vault/Plans/<action_id>-Plan.md
    """

    action_id: str
    created: datetime
    status: Literal["pending", "approved", "executing", "completed", "failed"]

    # MCP server details
    mcp_server: Literal["email", "linkedin", "browser"]
    tool_name: str
    tool_inputs: Dict[str, Any] = field(default_factory=dict)

    # Execution metadata
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Dry-run mode
    dry_run: bool = True

    def __post_init__(self):
        """Validate execution plan data."""
        if not self.action_id:
            raise ValueError("action_id is required")
        if not self.mcp_server:
            raise ValueError("mcp_server is required")
        if not self.tool_name:
            raise ValueError("tool_name is required")

    def mark_executing(self) -> None:
        """Mark execution plan as executing."""
        self.status = "executing"
        self.executed_at = datetime.now()

    def mark_completed(self) -> None:
        """Mark execution plan as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark execution plan as failed."""
        self.status = "failed"
        self.last_error = error
        self.retry_count += 1

    def can_retry(self) -> bool:
        """Check if execution plan can be retried."""
        return self.retry_count < self.max_retries

    def to_frontmatter_dict(self) -> dict:
        """Convert to YAML frontmatter dictionary for vault storage."""
        data = {
            "action_id": self.action_id,
            "created": self.created.isoformat(),
            "status": self.status,
            "mcp_server": self.mcp_server,
            "tool_name": self.tool_name,
            "tool_inputs": self.tool_inputs,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "dry_run": self.dry_run,
        }

        if self.last_error:
            data["last_error"] = self.last_error
        if self.executed_at:
            data["executed_at"] = self.executed_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict) -> "ExecutionPlanSchema":
        """Create ExecutionPlanSchema from YAML frontmatter dictionary."""
        return cls(
            action_id=data["action_id"],
            created=datetime.fromisoformat(data["created"]),
            status=data["status"],
            mcp_server=data["mcp_server"],
            tool_name=data["tool_name"],
            tool_inputs=data.get("tool_inputs", {}),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            last_error=data.get("last_error"),
            executed_at=datetime.fromisoformat(data["executed_at"]) if data.get("executed_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            dry_run=data.get("dry_run", True),
        )
