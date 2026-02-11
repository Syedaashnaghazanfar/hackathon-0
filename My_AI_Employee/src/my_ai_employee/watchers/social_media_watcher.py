"""
Social Media Watcher for Gold Tier AI Employee.

Orchestrates monitoring of Facebook, Instagram, and Twitter/X for social media interactions.
Extends APIBaseWatcher to follow the Silver tier watcher pattern.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from enum import Enum

from ..api_base_watcher import APIBaseWatcher
from ..models.watcher_state import WatcherStateSchema, compute_content_hash
from ..models.social_interaction import SocialInteractionSchema
from .facebook_monitor import FacebookMonitor
from .instagram_monitor import InstagramMonitor
from .twitter_monitor import TwitterMonitor
from .base_monitor import SessionExpiredError, PlatformError


logger = logging.getLogger(__name__)


class PlatformStatus(Enum):
    """Platform health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


class SocialMediaWatcher(APIBaseWatcher):
    """
    Orchestrator watcher for social media monitoring.

    Coordinates multiple platform monitors (Facebook, Instagram, Twitter)
    and creates action items in the vault for important interactions.

    Features:
    - Continuous polling loop (every 10 minutes by default)
    - Multi-platform monitoring (runs all enabled platforms)
    - Graceful degradation (one platform failure doesn't crash all)
    - Deduplication (prevents duplicate action items)
    - Health monitoring (tracks platform status)
    - Configurable platform enabling/disabling

    Usage:
        watcher = SocialMediaWatcher()
        watcher.run()  # Starts continuous loop
    """

    def __init__(
        self,
        check_interval: int = 600,  # 10 minutes
        enabled_platforms: Optional[List[str]] = None,
        vault_root: str = "AI_Employee_Vault"
    ):
        """
        Initialize the social media watcher.

        Args:
            check_interval: Seconds between checks (default: 600 = 10 min)
            enabled_platforms: List of platforms to monitor (default: all)
            vault_root: Path to Obsidian vault
        """
        super().__init__(check_interval=check_interval)

        self.watcher_name = "social_media"
        self.vault_root = Path(vault_root)

        # Determine enabled platforms
        self.enabled_platforms = enabled_platforms or ["facebook", "instagram", "twitter"]

        # Initialize platform monitors
        self.platforms = {
            "facebook": FacebookMonitor(),
            "instagram": InstagramMonitor(),
            "twitter": TwitterMonitor(),
        }

        # Platform health status
        self.platform_health: Dict[str, PlatformStatus] = {
            platform: PlatformStatus.HEALTHY
            for platform in self.enabled_platforms
        }

        # Initialize watcher state
        self.state = WatcherStateSchema(
            watcher_name="social_media",
            last_check=datetime.now(),
            health_status="healthy",
            processed_hashes=set(),
        )

        # Load existing state if available
        self._load_state()

    def _load_state(self) -> None:
        """Load watcher state from disk."""
        state_file = Path(".social_media_dedupe.json")

        if state_file.exists():
            try:
                import json
                with open(state_file, "r") as f:
                    data = json.load(f)
                self.state = WatcherStateSchema.from_dict(data)
                logger.info(f"Loaded existing state: {len(self.state.processed_hashes)} processed hashes")
            except Exception as e:
                logger.error(f"Error loading state: {e}")
                logger.info("Starting with fresh state")

    def _save_state(self) -> None:
        """Save watcher state to disk."""
        state_file = Path(".social_media_dedupe.json")

        try:
            import json
            with open(state_file, "w") as f:
                json.dump(self.state.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    async def check_for_new_items(self) -> None:
        """
        Check all enabled platforms for new interactions.

        This method:
        1. Runs each platform monitor
        2. Aggregates detected interactions
        3. Filters by priority (only HIGH/MEDIUM create action items)
        4. Deduplicates (prevents duplicate action items)
        5. Updates watcher state
        6. Handles errors gracefully (one platform fails → others continue)

        Raises:
            Exception: Only if ALL platforms fail
        """
        self.logger.info(f"Checking social media platforms: {self.enabled_platforms}")

        all_interactions = []
        platform_errors = {}

        # Check each platform
        for platform in self.enabled_platforms:
            if platform not in self.platforms:
                self.logger.warning(f"Unknown platform: {platform}")
                continue

            monitor = self.platforms[platform]
            self.logger.info(f"Checking {platform}...")

            try:
                # Check platform for interactions
                interactions, error = await monitor.safe_check()

                if error:
                    # Platform failed
                    platform_errors[platform] = str(error)
                    self.platform_health[platform] = PlatformStatus.DEGRADED
                    self.logger.error(f"{platform} check failed: {error}")

                elif interactions:
                    # Platform succeeded
                    all_interactions.extend(interactions)
                    self.platform_health[platform] = PlatformStatus.HEALTHY
                    self.logger.info(f"{platform}: {len(interactions)} interactions detected")

                else:
                    # No interactions (not an error)
                    self.platform_health[platform] = PlatformStatus.HEALTHY
                    self.logger.info(f"{platform}: No new interactions")

            except Exception as e:
                platform_errors[platform] = str(e)
                self.platform_health[platform] = PlatformStatus.FAILED
                self.logger.error(f"Unexpected error checking {platform}: {e}")

        # Update health status based on platform results
        failed_count = sum(1 for status in self.platform_health.values() if status == PlatformStatus.FAILED)
        degraded_count = sum(1 for status in self.platform_health.values() if status == PlatformStatus.DEGRADED)

        if failed_count == len(self.enabled_platforms):
            # All platforms failed
            self.state.mark_failure("All platforms failed")
            self.logger.error("All platforms failed - marking watcher as failed")

        elif failed_count > 0 or degraded_count > 0:
            # Some platforms failed/degraded
            self.state.mark_failure(f"{failed_count} failed, {degraded_count} degraded")
            self.logger.warning(f"Some platforms degraded: {failed_count} failed, {degraded_count} degraded")

        else:
            # All platforms healthy
            self.state.mark_success()

        # Process interactions (filter, deduplicate, create action items)
        await self._process_interactions(all_interactions)

        # Save state
        self._save_state()

        # Log summary
        self.logger.info(
            f"Check complete: {len(all_interactions)} interactions detected, "
            f"{len(platform_errors)} platforms had errors"
        )

    async def _process_interactions(self, interactions: List[SocialInteractionSchema]) -> None:
        """
        Process detected interactions.

        This method:
        1. Filters by priority (skip LOW priority)
        2. Deduplicates (skip if already processed)
        3. Creates action items in vault
        4. Updates processed hashes

        Args:
            interactions: List of detected social interactions
        """
        action_items_created = 0

        for interaction in interactions:
            # Skip LOW priority interactions
            if interaction.priority == "LOW":
                self.logger.debug(f"Skipping LOW priority interaction from {interaction.author}")
                continue

            # Check for duplicates
            content_hash = interaction.compute_content_hash()
            if self.state.is_duplicate(content_hash):
                self.logger.debug(f"Skipping duplicate interaction: {content_hash[:8]}")
                continue

            # Create action item
            try:
                # Get the platform monitor to create the action item
                monitor = self.platforms.get(interaction.platform)
                if monitor:
                    action_item_path = monitor.create_action_item(interaction)
                    action_items_created += 1

                    # Mark as processed
                    self.state.add_processed_hash(content_hash)
                    self.logger.info(f"Created action item: {action_item_path}")

            except Exception as e:
                self.logger.error(f"Error creating action item: {e}")

        self.logger.info(f"Created {action_items_created} action items")

    def run(self) -> None:
        """
        Run the social media watcher in a continuous loop.

        This method blocks and runs forever until interrupted.
        Checks all enabled platforms every check_interval seconds.
        """
        self.logger.info(f"Starting Social Media Watcher (interval: {self.check_interval}s)")
        self.logger.info(f"Enabled platforms: {self.enabled_platforms}")

        self.running = True

        while self.running:
            try:
                # Log heartbeat
                self._log_heartbeat()

                # Check for new interactions
                asyncio.run(self.check_for_new_items())

                # Wait for next check
                import time
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                self.logger.info("Received interrupt, shutting down...")
                self.running = False
                break

            except Exception as e:
                self.logger.error(f"Error in watcher loop: {e}")
                # Continue running despite errors
                import time
                time.sleep(self.check_interval)

        self.logger.info("Social Media Watcher stopped")

    def _log_heartbeat(self) -> None:
        """Log heartbeat message."""
        self.logger.info(
            f"Social Media Watcher running | "
            f"Platforms: {', '.join(self.enabled_platforms)} | "
            f"Status: {self.state.health_status} | "
            f"Processed: {len(self.state.processed_hashes)} items"
        )


# For compatibility with existing watcher pattern
def main():
    """CLI entry point for social media watcher."""
    import argparse
    from os import getenv

    parser = argparse.ArgumentParser(description="Social Media Watcher for Gold Tier AI Employee")
    parser.add_argument("--check-interval", type=int, default=600, help="Check interval in seconds")
    parser.add_argument("--platforms", type=str, help="Comma-separated list of platforms (facebook,instagram,twitter)")
    parser.add_argument("--init", action="store_true", help="Re-authenticate expired sessions")
    parser.add_argument("--generate-summary", action="store_true", help="Generate daily summary and exit")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Parse enabled platforms
    if args.platforms:
        enabled_platforms = [p.strip() for p in args.platforms.split(",")]
    else:
        # Check environment variables
        enabled_platforms = []
        if getenv("SOCIAL_FACEBOOK_ENABLED", "true").lower() == "true":
            enabled_platforms.append("facebook")
        if getenv("SOCIAL_INSTAGRAM_ENABLED", "true").lower() == "true":
            enabled_platforms.append("instagram")
        if getenv("SOCIAL_TWITTER_ENABLED", "true").lower() == "true":
            enabled_platforms.append("twitter")

    # Create and run watcher
    watcher = SocialMediaWatcher(
        check_interval=args.check_interval,
        enabled_platforms=enabled_platforms if enabled_platforms else None,
    )

    if args.init:
        # Re-authenticate sessions (not implemented yet)
        logger.warning("--init not yet implemented - please use social-media-browser-mcp skill")
        return

    if args.generate_summary:
        # Generate daily summary (not implemented yet)
        logger.warning("--generate-summary not yet implemented - coming in Phase 3")
        return

    # Run watcher
    watcher.run()


if __name__ == "__main__":
    main()
