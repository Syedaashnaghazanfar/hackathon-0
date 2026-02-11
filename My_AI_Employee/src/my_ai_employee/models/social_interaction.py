"""
Social Interaction data model for Gold Tier AI Employee.

Defines the schema for social media interactions (comments, DMs, mentions)
detected by the social media watcher.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, Dict, Any


@dataclass
class SocialInteractionSchema:
    """
    Social Media Interaction entity schema.

    Represents a single social media interaction (comment, DM, mention)
    detected by the social media watcher.

    Storage location: Created as markdown files in Needs_Action/ folder
    """

    # Platform and interaction type
    platform: Literal["facebook", "instagram", "twitter"]
    interaction_type: Literal["comment", "dm", "mention", "reply", "reaction"]

    # Content
    author: str  # Author username/handle
    author_url: Optional[str] = None  # Link to author profile
    content: str = ""  # Interaction text/content

    # Context
    post_url: Optional[str] = None  # URL of post/comment (if applicable)
    post_id: Optional[str] = None  # Platform-specific post ID
    parent_id: Optional[str] = None  # Parent comment/post ID (for replies)

    # Engagement metrics
    reactions: int = 0  # Number of reactions/likes
    comments: int = 0  # Number of comments
    shares: int = 0  # Number of shares/retweets

    # Timestamps
    timestamp: datetime = field(default_factory=datetime.now)
    detected_at: datetime = field(default_factory=datetime.now)

    # Priority classification
    priority: Literal["HIGH", "MEDIUM", "LOW"] = "LOW"
    priority_reason: Optional[str] = None  # Why this priority (e.g., "matched keyword: pricing")

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate social interaction data."""
        if not self.platform:
            raise ValueError("platform is required")
        if not self.interaction_type:
            raise ValueError("interaction_type is required")
        if not self.author:
            raise ValueError("author is required")

    def compute_content_hash(self) -> str:
        """
        Compute SHA256 hash for deduplication.

        Hash includes: platform + interaction_type + author + content + timestamp
        This prevents duplicate action items for the same interaction.
        """
        import hashlib

        # Create unique string for this interaction
        unique_string = f"{self.platform}:{self.interaction_type}:{self.author}:{self.content}:{self.timestamp.isoformat()}"

        # Compute SHA256 hash
        return hashlib.sha256(unique_string.encode()).hexdigest()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "platform": self.platform,
            "interaction_type": self.interaction_type,
            "author": self.author,
            "author_url": self.author_url,
            "content": self.content,
            "post_url": self.post_url,
            "post_id": self.post_id,
            "parent_id": self.parent_id,
            "reactions": self.reactions,
            "comments": self.comments,
            "shares": self.shares,
            "timestamp": self.timestamp.isoformat(),
            "detected_at": self.detected_at.isoformat(),
            "priority": self.priority,
            "priority_reason": self.priority_reason,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SocialInteractionSchema":
        """Create SocialInteractionSchema from dictionary."""
        return cls(
            platform=data["platform"],
            interaction_type=data["interaction_type"],
            author=data["author"],
            author_url=data.get("author_url"),
            content=data.get("content", ""),
            post_url=data.get("post_url"),
            post_id=data.get("post_id"),
            parent_id=data.get("parent_id"),
            reactions=data.get("reactions", 0),
            comments=data.get("comments", 0),
            shares=data.get("shares", 0),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            detected_at=datetime.fromisoformat(data["detected_at"]) if data.get("detected_at") else datetime.now(),
            priority=data.get("priority", "LOW"),
            priority_reason=data.get("priority_reason"),
            metadata=data.get("metadata", {}),
        )

    def to_action_item_frontmatter(self) -> dict:
        """
        Convert to frontmatter format for vault action items.

        Returns a dict suitable for YAML frontmatter in Needs_Action/ markdown files.
        """
        return {
            "type": "social_media",
            "source": self.platform,
            "interaction_type": self.interaction_type,
            "author": self.author,
            "author_url": self.author_url,
            "priority": self.priority,
            "received": self.timestamp.isoformat(),
            "status": "pending",
            "source_id": self.post_id or self.compute_content_hash()[:8],
            "subject": f"{self.platform} {self.interaction_type} from {self.author}",
            "tags": [self.platform, self.interaction_type, "social_media"],
            "platform": self.platform,
            "content_preview": self.content[:100] + "..." if len(self.content) > 100 else self.content,
        }
