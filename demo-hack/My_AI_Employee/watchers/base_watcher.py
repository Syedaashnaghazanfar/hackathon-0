"""
Base watcher abstract class for all watcher implementations.

Provides common functionality for file system monitoring using watchdog.
"""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import logging
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class BaseWatcher(FileSystemEventHandler, ABC):
    """
    Abstract base class for all watcher implementations.

    Subclasses must implement:
    - check_for_updates(): Return list of new items to process
    - create_action_file(): Create .md file in Needs_Action folder
    """

    def __init__(self, vault_path: str | Path, check_interval: int = 60):
        """
        Initialize base watcher.

        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between checks (for polling mode)
        """
        super().__init__()
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logger for this watcher."""
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.

        Returns:
            List of new items to process
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Optional[Path]:
        """
        Create .md file in Needs_Action folder.

        Args:
            item: Item to process

        Returns:
            Path to created file, or None if creation failed
        """
        pass

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Called when a file or directory is created.

        Override this in subclasses for specific behavior.

        Args:
            event: FileSystemEvent object
        """
        if not event.is_directory:
            self.logger.info(f"File created: {event.src_path}")

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Called when a file or directory is modified.

        Args:
            event: FileSystemEvent object
        """
        pass  # Override in subclasses if needed

    def on_deleted(self, event: FileSystemEvent) -> None:
        """
        Called when a file or directory is deleted.

        Args:
            event: FileSystemEvent object
        """
        pass  # Override in subclasses if needed

    def validate_vault_structure(self) -> bool:
        """
        Validate that vault has required structure.

        Returns:
            True if valid, False otherwise
        """
        required_paths = [
            self.vault_path / 'Needs_Action',
            self.vault_path / 'Done',
            self.vault_path / 'Dashboard.md',
            self.vault_path / 'Company_Handbook.md'
        ]

        for path in required_paths:
            if not path.exists():
                self.logger.error(f"Required path missing: {path}")
                return False

        return True

    def run(self) -> None:
        """
        Main polling loop for the watcher.

        Continuously checks for updates and creates action files.
        This method runs indefinitely until interrupted.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')

        while True:
            try:
                self.logger.info('Checking for new items...')
                items = self.check_for_updates()

                if items:
                    self.logger.info(f'Found {len(items)} new items')
                    for item in items:
                        try:
                            result = self.create_action_file(item)
                            if result:
                                self.logger.info(f'Created action file: {result.name}')
                        except Exception as e:
                            self.logger.error(f'Error creating action file: {e}')
                else:
                    self.logger.info('Found 0 new items')

            except KeyboardInterrupt:
                self.logger.info('Watcher stopped by user')
                break
            except Exception as e:
                self.logger.error(f'Error in watcher loop: {e}')

            time.sleep(self.check_interval)
