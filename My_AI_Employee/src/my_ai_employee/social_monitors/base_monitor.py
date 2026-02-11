"""
Abstract base class for social media platform monitors.

Provides a consistent interface for Facebook, Instagram, and Twitter monitors
to detect social media interactions (comments, DMs, mentions).
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from ..models.social_interaction import SocialInteractionSchema


logger = logging.getLogger(__name__)


class BaseSocialMonitor(ABC):
    """
    Abstract base class for social media platform monitors.

    All platform monitors (Facebook, Instagram, Twitter) must inherit from this
    class and implement the required methods.
    """

    # Platform identifier (must be defined by subclasses)
    PLATFORM: str = None

    # Session directory (where browser session data is stored)
    SESSION_DIR: Path = None

    def __init__(self, session_dir: Optional[Path] = None):
        """
        Initialize the social media monitor.

        Args:
            session_dir: Path to platform-specific session directory
                        (e.g., .social_session/facebook/)
        """
        if not self.PLATFORM:
            raise ValueError(f"{self.__class__.__name__} must define PLATFORM class attribute")

        self.session_dir = session_dir or self._get_default_session_dir()
        self.logger = logging.getLogger(f"social_media.{self.PLATFORM}")

    def _get_default_session_dir(self) -> Path:
        """
        Get the default session directory for this platform.

        Returns:
            Path to platform-specific session directory
        """
        return Path(f".social_session/{self.PLATFORM}")

    def validate_session(self) -> tuple[bool, Optional[str]]:
        """
        Validate that the browser session exists and is recent enough.

        A session is considered valid if:
        1. The session directory exists
        2. It contains a cookies file or browser state
        3. The session was created/updated within the last 30 days

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if session is valid, False otherwise
            - error_message: Error message if invalid, None otherwise
        """
        # Check if session directory exists
        if not self.session_dir.exists():
            return False, f"Session directory not found: {self.session_dir}"

        # Check if cookies file exists (indicates authenticated session)
        cookies_file = self.session_dir / "cookies.json"
        if not cookies_file.exists():
            # Alternative: check for storage.json (Chromium session)
            storage_file = self.session_dir / "Storage" / "https"
            if not storage_file.exists():
                return False, f"No session data found in {self.session_dir}"

        # Check session age (last modified time)
        session_age_days = (datetime.now() - datetime.fromtimestamp(self.session_dir.stat().st_mtime)).days

        # Sessions older than 30 days may be expired
        if session_age_days > 30:
            return False, f"Session expired (last used {session_age_days} days ago)"

        # Session is valid
        self.logger.info(f"Session validated: {self.session_dir} ({session_age_days} days old)")
        return True, None

    @abstractmethod
    async def check_notifications(self) -> List[SocialInteractionSchema]:
        """
        Check for new notifications/interactions on this platform.

        This method must:
        1. Launch browser with persistent context (using session_dir)
        2. Navigate to platform's notification/notification center
        3. Extract new interactions since last check
        4. Return list of SocialInteractionSchema objects

        Returns:
            List of detected social interactions

        Raises:
            SessionExpiredError: If session is not valid or expired
            PlatformError: If platform navigation or detection fails
        """
        pass

    @abstractmethod
    def extract_interactions(self, raw_data: dict) -> List[SocialInteractionSchema]:
        """
        Extract interaction data from raw platform data.

        This method must parse platform-specific data (HTML, JSON, etc.)
        and convert it to SocialInteractionSchema objects.

        Args:
            raw_data: Raw data from platform (HTML, JSON, etc.)

        Returns:
            List of SocialInteractionSchema objects

        Raises:
            ValueError: If raw_data is malformed or missing required fields
        """
        pass

    def create_action_item(self, interaction: SocialInteractionSchema) -> str:
        """
        Create a vault action item for a social media interaction.

        This method creates a markdown file in the Needs_Action/ folder
        with appropriate frontmatter.

        Args:
            interaction: SocialInteractionSchema object

        Returns:
            Path to created action item file

        Raises:
            IOError: If vault write fails
        """
        from ..utils.vault_ops import write_markdown_with_frontmatter
        from ..utils.deduplication import compute_content_hash

        # Generate filename
        timestamp_str = interaction.detected_at.strftime("%Y%m%d-%H%M%S")
        content_hash = compute_content_hash(
            interaction.content,
            {"author": interaction.author, "timestamp": interaction.timestamp.isoformat()}
        )
        filename = f"{timestamp_str}-socialmedia-{content_hash[:8]}.md"

        # Get frontmatter from interaction
        frontmatter = interaction.to_action_item_frontmatter()

        # Generate markdown content
        content = f"""# {interaction.platform} {interaction.interaction_type} from {interaction.author}

**Author:** {interaction.author}
{"**Author URL:** " + interaction.author_url if interaction.author_url else ""}
**Platform:** {interaction.platform}
**Type:** {interaction.interaction_type}
**Detected:** {interaction.detected_at.strftime("%Y-%m-%d %H:%M:%S")}
**Priority:** {interaction.priority}
{f"**Priority Reason:** {interaction.priority_reason}" if interaction.priority_reason else ""}

{"**Post URL:** " + interaction.post_url if interaction.post_url else ""}

## Content

{interaction.content}

{"## Engagement Metrics" if interaction.reactions or interaction.comments or interaction.shares else ""}
{f"- **Reactions:** {interaction.reactions}" if interaction.reactions else ""}
{f"- **Comments:** {interaction.comments}" if interaction.comments else ""}
{f"- **Shares:** {interaction.shares}" if interaction.shares else ""}

{"## Metadata" if interaction.metadata else ""}
{chr(10).join([f"- **{k}:** {v}" for k, v in interaction.metadata.items()]) if interaction.metadata else ""}

---

## Suggested Actions

1. Review this interaction
2. Determine if response is needed
3. If response needed, move to Pending_Approval/
4. Otherwise, move to Done/
"""

        # Write to vault
        vault_path = Path("AI_Employee_Vault/Needs_Action") / filename
        write_markdown_with_frontmatter(vault_path, frontmatter, content)

        self.logger.info(f"Created action item: {vault_path}")
        return str(vault_path)

    async def safe_check(self) -> tuple[List[SocialInteractionSchema], Optional[Exception]]:
        """
        Safely check for notifications with error handling.

        This wrapper method:
        1. Validates session before checking
        2. Calls check_notifications()
        3. Handles exceptions gracefully
        4. Returns results or error

        Returns:
            Tuple of (interactions, error)
            - interactions: List of detected interactions (empty if error)
            - error: Exception if check failed, None otherwise
        """
        # Validate session
        is_valid, error_msg = self.validate_session()
        if not is_valid:
            self.logger.error(f"Session validation failed: {error_msg}")
            return [], SessionExpiredError(error_msg)

        try:
            # Check for notifications
            interactions = await self.check_notifications()
            self.logger.info(f"Detected {len(interactions)} new interactions on {self.PLATFORM}")
            return interactions, None

        except Exception as e:
            self.logger.error(f"Error checking {self.PLATFORM} notifications: {e}")
            return [], e


class SessionExpiredError(Exception):
    """Raised when social media session is expired or invalid."""

    pass


class PlatformError(Exception):
    """Raised when platform navigation or detection fails."""

    pass
