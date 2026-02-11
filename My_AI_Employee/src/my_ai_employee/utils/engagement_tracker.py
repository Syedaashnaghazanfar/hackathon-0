"""
Engagement Tracker for Gold Tier AI Employee.

Tracks social media engagement metrics in rolling time windows.
Detects viral activity when thresholds are exceeded.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict

from ..models.social_interaction import SocialInteractionSchema


logger = logging.getLogger(__name__)


@dataclass
class EngagementMetrics:
    """
    Engagement metrics for a platform in a time window.

    Attributes:
        platform: Platform name (facebook, instagram, twitter)
        window_start: Start of time window
        window_end: End of time window
        comment_count: Number of comments detected
        dm_count: Number of DMs detected
        mention_count: Number of mentions detected
        reaction_count: Number of reactions detected
        total_interactions: Total interactions in window
        threshold: Viral threshold for this platform
        threshold_exceeded: Whether threshold was exceeded
    """
    platform: str
    window_start: datetime
    window_end: datetime
    comment_count: int = 0
    dm_count: int = 0
    mention_count: int = 0
    reaction_count: int = 0
    total_interactions: int = 0
    threshold: int = 0
    threshold_exceeded: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "platform": self.platform,
            "window_start": self.window_start.isoformat(),
            "window_end": self.window_end.isoformat(),
            "comment_count": self.comment_count,
            "dm_count": self.dm_count,
            "mention_count": self.mention_count,
            "reaction_count": self.reaction_count,
            "total_interactions": self.total_interactions,
            "threshold": self.threshold,
            "threshold_exceeded": self.threshold_exceeded,
        }


class EngagementTracker:
    """
    Tracks social media engagement metrics and detects viral activity.

    Features:
    - Rolling window tracking (configurable time windows)
    - Platform-specific thresholds
    - Viral alert generation
    - Metric aggregation and reporting

    Usage:
        tracker = EngagementTracker()
        tracker.track_interactions(interactions)
        metrics = tracker.get_metrics("twitter", hours=1)
        if metrics.threshold_exceeded:
            # Create viral alert
    """

    # Default thresholds (can be overridden by environment variables)
    DEFAULT_THRESHOLDS = {
        "facebook": 10,   # 10 reactions/comments
        "instagram": 5,    # 5 comments
        "twitter": 3,      # 3 mentions
    }

    def __init__(self, vault_root: str = "AI_Employee_Vault"):
        """
        Initialize the engagement tracker.

        Args:
            vault_root: Path to Obsidian vault root
        """
        self.vault_root = vault_root

        # Load thresholds from environment or use defaults
        self.thresholds = self._load_thresholds()

        # Rolling window tracking
        # Structure: {platform: {(window_start, window_end): interaction_count}}
        self.interaction_windows: Dict[str, Dict[tuple, int]] = defaultdict(lambda: defaultdict(int))

        # Detailed tracking by interaction type
        # Structure: {platform: {interaction_type: count}}
        self.interaction_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        logger.info(f"EngagementTracker initialized with thresholds: {self.thresholds}")

    def _load_thresholds(self) -> Dict[str, int]:
        """
        Load engagement thresholds from environment variables.

        Environment variables:
        - SOCIAL_FB_REACTION_THRESHOLD (default: 10)
        - SOCIAL_IG_COMMENT_THRESHOLD (default: 5)
        - SOCIAL_TWITTER_MENTION_THRESHOLD (default: 3)

        Returns:
            Dict mapping platform to threshold value
        """
        from os import getenv

        thresholds = self.DEFAULT_THRESHOLDS.copy()

        # Override from environment if set
        fb_threshold = getenv("SOCIAL_FB_REACTION_THRESHOLD")
        if fb_threshold:
            thresholds["facebook"] = int(fb_threshold)

        ig_threshold = getenv("SOCIAL_IG_COMMENT_THRESHOLD")
        if ig_threshold:
            thresholds["instagram"] = int(ig_threshold)

        tw_threshold = getenv("SOCIAL_TWITTER_MENTION_THRESHOLD")
        if tw_threshold:
            thresholds["twitter"] = int(tw_threshold)

        return thresholds

    def track_interactions(self, interactions: List[SocialInteractionSchema]) -> None:
        """
        Track social media interactions for viral detection.

        This method:
        1. Groups interactions by platform
        2. Updates rolling window counts
        3. Checks if thresholds are exceeded
        4. Cleans up old data outside rolling window

        Args:
            interactions: List of social interactions to track
        """
        current_time = datetime.now()

        # Group interactions by platform
        by_platform = defaultdict(list)
        for interaction in interactions:
            by_platform[interaction.platform].append(interaction)

        # Track each platform
        for platform, platform_interactions in by_platform.items():
            # Update interaction counts
            for interaction in platform_interactions:
                interaction_type = interaction.interaction_type
                self.interaction_counts[platform][interaction_type] += 1

            # Get threshold for this platform
            threshold = self.thresholds.get(platform, 10)

            # Calculate time window (1 hour rolling)
            window_start = current_time - timedelta(hours=1)
            window_end = current_time
            window_key = (window_start, window_end)

            # Update rolling window count
            self.interaction_windows[platform][window_key] += len(platform_interactions)

            # Check if threshold exceeded
            total_in_window = self.interaction_windows[platform][window_key]
            if total_in_window > threshold:
                logger.warning(
                    f"Platform '{platform}' exceeded viral threshold: "
                    f"{total_in_window} interactions > threshold of {threshold}"
                )

        # Clean up old windows (older than 1 hour)
        self._cleanup_old_windows(current_time)

    def get_metrics(
        self,
        platform: str,
        hours: int = 1
    ) -> Optional[EngagementMetrics]:
        """
        Get engagement metrics for a platform in a time window.

        Args:
            platform: Platform name (facebook, instagram, twitter)
            hours: Time window in hours (default: 1)

        Returns:
            EngagementMetrics object, or None if platform not tracked
        """
        current_time = datetime.now()
        window_start = current_time - timedelta(hours=hours)
        window_end = current_time
        window_key = (window_start, window_end)

        # Get total interactions in window
        total_interactions = self.interaction_windows[platform][window_key]

        # Get interaction type counts
        interaction_counts = self.interaction_counts.get(platform, {})

        # Create metrics object
        metrics = EngagementMetrics(
            platform=platform,
            window_start=window_start,
            window_end=window_end,
            comment_count=interaction_counts.get("comment", 0),
            dm_count=interaction_counts.get("dm", 0),
            mention_count=interaction_counts.get("mention", 0),
            reaction_count=interaction_counts.get("reaction", 0),
            total_interactions=total_interactions,
            threshold=self.thresholds.get(platform, 0),
            threshold_exceeded=total_interactions > self.thresholds.get(platform, 0)
        )

        return metrics

    def check_viral_status(
        self,
        platform: str,
        hours: int = 1
    ) -> tuple[bool, Optional[EngagementMetrics]]:
        """
        Check if a platform has exceeded its viral threshold.

        Args:
            platform: Platform name
            hours: Time window in hours (default: 1)

        Returns:
            Tuple of (is_viral, metrics)
            - is_viral: True if threshold exceeded
            - metrics: EngagementMetrics object (or None if error)
        """
        try:
            metrics = self.get_metrics(platform, hours)
            is_viral = metrics.threshold_exceeded if metrics else False

            if is_viral:
                logger.warning(
                    f"Viral activity detected on {platform}: "
                    f"{metrics.total_interactions} interactions > {metrics.threshold}"
                )

            return is_viral, metrics

        except Exception as e:
            logger.error(f"Error checking viral status for {platform}: {e}")
            return False, None

    def get_all_platforms_status(self, hours: int = 1) -> Dict[str, Dict]:
        """
        Get viral status for all platforms.

        Args:
            hours: Time window in hours (default: 1)

        Returns:
            Dict mapping platform to status dict:
            {
                "platform": "twitter",
                "is_viral": true,
                "metrics": {...}
            }
        """
        status = {}

        for platform in self.thresholds.keys():
            is_viral, metrics = self.check_viral_status(platform, hours)

            status[platform] = {
                "platform": platform,
                "is_viral": is_viral,
                "metrics": metrics.to_dict() if metrics else None,
                "threshold": self.thresholds[platform]
            }

        return status

    def _cleanup_old_windows(self, current_time: datetime) -> None:
        """
        Clean up interaction windows older than 1 hour.

        Args:
            current_time: Current time
        """
        cutoff_time = current_time - timedelta(hours=1)

        for platform in list(self.interaction_windows.keys()):
            # Remove old windows
            old_windows = [
                window_key
                for window_key in self.interaction_windows[platform].keys()
                if window_key[1] < cutoff_time  # window_key[1] is window_end
            ]

            for window_key in old_windows:
                del self.interaction_windows[platform][window_key]

            if old_windows:
                self.logger.debug(
                    f"Cleaned up {len(old_windows)} old interaction windows for {platform}"
                )

    def create_viral_alert(
        self,
        platform: str,
        metrics: EngagementMetrics,
        top_interactions: List[SocialInteractionSchema] = None
    ) -> SocialInteractionSchema:
        """
        Create a viral alert interaction.

        Args:
            platform: Platform that went viral
            metrics: Engagement metrics showing viral activity
            top_interactions: Top interactions to include in alert (optional)

        Returns:
            SocialInteractionSchema object representing the viral alert
        """
        # Generate alert content
        content = f"⚠️ VIRAL ALERT on {platform.capitalize()}\n\n"
        content += f"**Total Interactions:** {metrics.total_interactions}\n"
        content += f"**Threshold:** {metrics.threshold}\n"
        content += f"**Exceeded By:** {metrics.total_interactions - metrics.threshold} interactions\n"
        content += f"**Time Window:** {metrics.window_start.strftime('%Y-%m-%d %H:%M')} to {metrics.window_end.strftime('%Y-%m-%d %H:%M')}\n\n"

        content += "**Breakdown:**\n"
        if metrics.comment_count > 0:
            content += f"- Comments: {metrics.comment_count}\n"
        if metrics.dm_count > 0:
            content += f"- DMs: {metrics.dm_count}\n"
        if metrics.mention_count > 0:
            content += f"- Mentions: {metrics.mention_count}\n"
        if metrics.reaction_count > 0:
            content += f"- Reactions: {metrics.reaction_count}\n"

        if top_interactions:
            content += f"\n**Top {min(len(top_interactions), 5)} Recent Interactions:**\n"
            for i, interaction in enumerate(top_interactions[:5], 1):
                content += f"{i}. @{interaction.author}: {interaction.content[:50]}...\n"

        content += "\n**Suggested Actions:**\n"
        content += "1. Review the viral activity immediately\n"
        content += "2. Respond to high-priority interactions\n"
        content += "3. Consider posting follow-up content to capitalize on engagement\n"

        # Create viral alert interaction
        alert = SocialInteractionSchema(
            platform=platform,
            interaction_type="mention",  # Viral alerts are treated as mentions
            author="System",  # System-generated
            content=content,
            timestamp=datetime.now(),
            detected_at=datetime.now(),
            priority="HIGH",
            priority_reason=f"Viral activity: {metrics.total_interactions} interactions exceeds threshold of {metrics.threshold}",
            metadata={
                "viral_type": "platform_threshold_exceeded",
                "total_interactions": metrics.total_interactions,
                "threshold": metrics.threshold,
                "time_window_hours": 1,
            }
        )

        return alert

    def reset_tracking(self, platform: Optional[str] = None) -> None:
        """
        Reset tracking data for a platform or all platforms.

        Args:
            platform: Platform to reset (None = reset all)
        """
        if platform:
            if platform in self.interaction_windows:
                del self.interaction_windows[platform]
            if platform in self.interaction_counts:
                del self.interaction_counts[platform]
            logger.info(f"Reset tracking data for {platform}")
        else:
            self.interaction_windows.clear()
            self.interaction_counts.clear()
            logger.info("Reset tracking data for all platforms")
