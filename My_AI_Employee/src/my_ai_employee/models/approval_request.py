"""
Approval Request data model for Silver Tier AI Employee.

Defines the schema for approval requests created by the triage skill and processed by the
approval workflow manager skill.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, Dict, Any


@dataclass
class ApprovalRequestSchema:
    """
    Approval Request entity schema.

    Storage location:
    - Pending: AI_Employee_Vault/Pending_Approval/<action_id>.md
    - Approved: AI_Employee_Vault/Approved/<action_id>.md
    - Rejected: AI_Employee_Vault/Rejected/<action_id>.md
    """

    # Required fields (no defaults)
    action_id: str
    action_type: Literal["send_email", "publish_linkedin_post", "send_whatsapp_message", "browser_automation"]
    created: datetime
    status: Literal["pending", "approved", "rejected"]
    risk_level: Literal["low", "medium", "high"]
    tool_name: str

    # Optional fields (with defaults)
    risk_factors: list[str] = field(default_factory=list)
    tool_inputs_preview: Dict[str, Any] = field(default_factory=dict)

    # Approval metadata
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    # Execution tracking
    execution_plan_path: Optional[str] = None

    def __post_init__(self):
        """Validate approval request data."""
        if not self.action_id:
            raise ValueError("action_id is required")
        if not self.tool_name:
            raise ValueError("tool_name is required")

    def approve(self, approved_by: str) -> None:
        """Mark approval request as approved."""
        self.status = "approved"
        self.approved_by = approved_by
        self.approved_at = datetime.now()

    def reject(self, rejected_by: str, reason: str) -> None:
        """Mark approval request as rejected."""
        self.status = "rejected"
        self.approved_by = rejected_by  # Reuse field for rejected_by
        self.approved_at = datetime.now()
        self.rejection_reason = reason

    def to_frontmatter_dict(self) -> dict:
        """Convert to YAML frontmatter dictionary for vault storage."""
        data = {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "created": self.created.isoformat(),
            "status": self.status,
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "tool_name": self.tool_name,
            "tool_inputs_preview": self.tool_inputs_preview,
        }

        if self.approved_by:
            data["approved_by"] = self.approved_by
        if self.approved_at:
            data["approved_at"] = self.approved_at.isoformat()
        if self.rejection_reason:
            data["rejection_reason"] = self.rejection_reason
        if self.execution_plan_path:
            data["execution_plan_path"] = self.execution_plan_path

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict) -> "ApprovalRequestSchema":
        """Create ApprovalRequestSchema from YAML frontmatter dictionary."""
        return cls(
            action_id=data["action_id"],
            action_type=data["action_type"],
            created=datetime.fromisoformat(data["created"]),
            status=data["status"],
            risk_level=data["risk_level"],
            risk_factors=data.get("risk_factors", []),
            tool_name=data["tool_name"],
            tool_inputs_preview=data.get("tool_inputs_preview", {}),
            approved_by=data.get("approved_by"),
            approved_at=datetime.fromisoformat(data["approved_at"]) if data.get("approved_at") else None,
            rejection_reason=data.get("rejection_reason"),
            execution_plan_path=data.get("execution_plan_path"),
        )
