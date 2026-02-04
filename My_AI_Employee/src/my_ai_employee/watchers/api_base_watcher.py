"""
API-based base watcher for Silver Tier AI Employee.

Provides common functionality for API watchers (Gmail, WhatsApp, LinkedIn).
Different from filesystem BaseWatcher which uses watchdog events.
"""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

from my_ai_employee.config import get_config
from my_ai_employee.utils import setup_logging, log_heartbeat


class APIBaseWatcher(ABC):
    """
    Abstract base class for API-based watchers.

    Provides common functionality:
    - Heartbeat logging
    - Check interval management
    - Vault path resolution
    - Graceful shutdown handling
    """

    def __init__(self, watcher_name: str, check_interval: Optional[int] = None):
        """
        Initialize API base watcher.

        Args:
            watcher_name: Name of the watcher (e.g., "gmail_watcher", "whatsapp_watcher")
            check_interval: Polling interval in seconds (defaults to CHECK_INTERVAL from config)
        """
        self.watcher_name = watcher_name
        self.config = get_config()
        self.check_interval = check_interval or self.config.check_interval
        self.vault_path = self.config.vault_root
        self.running = False

        # Setup logging
        self.logger = setup_logging(watcher_name, log_level=self.config.log_level)

    @abstractmethod
    def check_for_new_items(self) -> None:
        """
        Check for new items from the monitored source.

        Must be implemented by subclasses to define source-specific logic.

        Example implementation:
            def check_for_new_items(self):
                # Fetch new emails from Gmail API
                # Create action items in /Needs_Action/
                pass
        """
        pass

    def run(self) -> None:
        """
        Start the watcher loop.

        Continuously checks for new items at the configured interval.
        Handles graceful shutdown and error recovery.
        """
        self.running = True
        self.logger.info(f"{self.watcher_name} started (check interval: {self.check_interval}s)")

        if self.config.dry_run:
            self.logger.warning(f"{self.watcher_name} running in DRY-RUN mode. No real actions will be executed.")

        try:
            while self.running:
                try:
                    # Log heartbeat for health monitoring
                    log_heartbeat(self.logger, self.watcher_name)

                    # Check for new items
                    self.check_for_new_items()

                    # Wait for next check
                    time.sleep(self.check_interval)

                except KeyboardInterrupt:
                    self.logger.info(f"{self.watcher_name} interrupted by user")
                    self.stop()
                    break

                except Exception as e:
                    self.logger.error(f"Error in {self.watcher_name}: {e}", exc_info=True)
                    # Continue running after error (graceful degradation)
                    time.sleep(self.check_interval)

        finally:
            self.logger.info(f"{self.watcher_name} stopped")

    def stop(self) -> None:
        """
        Stop the watcher gracefully.
        """
        self.running = False
        self.logger.info(f"{self.watcher_name} stopping...")

    def get_needs_action_path(self) -> Path:
        """
        Get path to Needs_Action folder.

        Returns:
            Path to /Needs_Action/ folder
        """
        return self.vault_path / "Needs_Action"

    def create_action_item_filename(self, source_id: str, source_type: str) -> str:
        """
        Generate standardized action item filename.

        Args:
            source_id: Unique identifier from source (email ID, message hash, etc.)
            source_type: Source type (email, whatsapp, linkedin)

        Returns:
            Filename in format: YYYYMMDD-HHMMSS-{source_type}-{source_id}.md

        Example:
            >>> watcher.create_action_item_filename("abc123", "email")
            '20260122-103045-email-abc123.md'
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Sanitize source_id (remove special characters)
        safe_source_id = "".join(c for c in source_id if c.isalnum() or c in "-_")[:20]
        return f"{timestamp}-{source_type}-{safe_source_id}.md"
