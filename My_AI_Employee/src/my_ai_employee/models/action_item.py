"""
Action Item data model for Silver Tier AI Employee.

Defines the schema for action items created by watchers (Gmail, WhatsApp, LinkedIn, filesystem).
Includes Bronze tier fields plus Silver tier extensions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, List


@dataclass
class ActionItemSchema:
    """
    Action Item entity schema.

    Storage location: AI_Employee_Vault/Needs_Action/<timestamp>-<source_id>.md
    """

    # Bronze tier fields
    type: Literal["email", "whatsapp", "linkedin", "file_drop"]
    received: datetime
    status: Literal["pending", "processed"]
    priority: Literal["high", "medium", "low", "auto"]
    source_id: str

    # Silver tier additions
    sender: str
    subject: str
    content_preview: str  # First 500 chars
    tags: List[str] = field(default_factory=list)

    # Validation rules
    def __post_init__(self):
        """Validate action item data."""
        if not self.sender:
            raise ValueError("Sender is required")
        if not self.subject:
            raise ValueError("Subject is required")
        if len(self.content_preview) > 500:
            self.content_preview = self.content_preview[:500]

        # Auto-detect priority keywords
        if self.priority == "auto":
            self.priority = self._detect_priority()

    def _detect_priority(self) -> Literal["high", "medium", "low"]:
        """Auto-detect priority from subject and content."""
        urgent_keywords = ["urgent", "asap", "emergency", "critical", "immediate"]
        medium_keywords = ["important", "review", "approve", "decision"]

        text = f"{self.subject} {self.content_preview}".lower()

        if any(keyword in text for keyword in urgent_keywords):
            return "high"
        elif any(keyword in text for keyword in medium_keywords):
            return "medium"
        else:
            return "low"

    def to_frontmatter_dict(self) -> dict:
        """Convert to YAML frontmatter dictionary for vault storage."""
        return {
            "type": self.type,
            "received": self.received.isoformat(),
            "status": self.status,
            "priority": self.priority,
            "source_id": self.source_id,
            "sender": self.sender,
            "subject": self.subject,
            "tags": self.tags,
        }

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content_preview: str) -> "ActionItemSchema":
        """Create ActionItemSchema from YAML frontmatter dictionary."""
        return cls(
            type=data["type"],
            received=datetime.fromisoformat(data["received"]),
            status=data["status"],
            priority=data["priority"],
            source_id=data["source_id"],
            sender=data["sender"],
            subject=data["subject"],
            content_preview=content_preview,
            tags=data.get("tags", []),
        )
