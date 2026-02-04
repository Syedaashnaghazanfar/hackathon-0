"""
Watcher State data model for Silver Tier AI Employee.

Defines the schema for watcher state tracking (deduplication, health monitoring).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional, Set


@dataclass
class WatcherStateSchema:
    """
    Watcher State entity schema.

    Storage location: ./<watcher_name>_dedupe.json (e.g., .gmail_dedupe.json)
    """

    watcher_name: Literal["gmail", "whatsapp", "linkedin", "filesystem"]
    last_check: datetime
    health_status: Literal["healthy", "degraded", "failed"]

    # Deduplication (SHA256 hashes of processed messages)
    processed_hashes: Set[str] = field(default_factory=set)

    # Health metadata
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    last_success: Optional[datetime] = None

    # Session persistence (for WhatsApp)
    session_path: Optional[str] = None
    session_authenticated: bool = False

    def __post_init__(self):
        """Validate watcher state data."""
        if not self.watcher_name:
            raise ValueError("watcher_name is required")

    def mark_success(self) -> None:
        """Mark watcher check as successful."""
        self.health_status = "healthy"
        self.consecutive_failures = 0
        self.last_error = None
        self.last_success = datetime.now()
        self.last_check = datetime.now()

    def mark_failure(self, error: str) -> None:
        """Mark watcher check as failed."""
        self.consecutive_failures += 1
        self.last_error = error
        self.last_check = datetime.now()

        # Update health status based on consecutive failures
        if self.consecutive_failures >= 3:
            self.health_status = "failed"
        else:
            self.health_status = "degraded"

    def add_processed_hash(self, content_hash: str) -> None:
        """Add message hash to deduplication set."""
        self.processed_hashes.add(content_hash)

    def is_duplicate(self, content_hash: str) -> bool:
        """Check if message hash has been processed."""
        return content_hash in self.processed_hashes

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "watcher_name": self.watcher_name,
            "last_check": self.last_check.isoformat(),
            "health_status": self.health_status,
            "processed_hashes": list(self.processed_hashes),
            "consecutive_failures": self.consecutive_failures,
            "last_error": self.last_error,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "session_path": self.session_path,
            "session_authenticated": self.session_authenticated,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WatcherStateSchema":
        """Create WatcherStateSchema from dictionary."""
        return cls(
            watcher_name=data["watcher_name"],
            last_check=datetime.fromisoformat(data["last_check"]),
            health_status=data["health_status"],
            processed_hashes=set(data.get("processed_hashes", [])),
            consecutive_failures=data.get("consecutive_failures", 0),
            last_error=data.get("last_error"),
            last_success=datetime.fromisoformat(data["last_success"]) if data.get("last_success") else None,
            session_path=data.get("session_path"),
            session_authenticated=data.get("session_authenticated", False),
        )
