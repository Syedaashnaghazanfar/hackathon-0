"""Base class for filesystem watchers.

Defines the common interface and patterns for watchers that monitor
directories and generate action items.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEventHandler


class BaseWatcher(FileSystemEventHandler, ABC):
    """Abstract base class for filesystem watchers.

    Extends watchdog's FileSystemEventHandler to provide a common
    pattern for watchers that create action items from file events.
    """

    def __init__(
        self,
        vault_path: Path | str,
        watch_folder: Path | str,
        watch_mode: str = "events",
    ):
        """Initialize the base watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            watch_folder: Path to the folder to watch for file drops
            watch_mode: Either "events" (default) or "polling"
        """
        super().__init__()

        if isinstance(vault_path, str):
            vault_path = Path(vault_path)
        if isinstance(watch_folder, str):
            watch_folder = Path(watch_folder)

        self.vault_path = vault_path
        self.watch_folder = watch_folder
        self.watch_mode = watch_mode

        # Validate vault structure
        self._validate_vault()

    def _validate_vault(self) -> None:
        """Validate that the vault has the required structure.

        Raises:
            ValueError: If vault structure is invalid
        """
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        needs_action = self.vault_path / "Needs_Action"
        if not needs_action.exists():
            raise ValueError(
                f"Needs_Action folder not found in vault: {needs_action}"
            )

    @abstractmethod
    def run(self) -> None:
        """Start the watcher and run until interrupted.

        This method should set up the observer, start watching,
        and handle graceful shutdown.
        """
        pass

    @abstractmethod
    def _create_action_item(self, file_path: Path) -> Optional[Path]:
        """Create an action item for a dropped file.

        Args:
            file_path: Path to the file that was dropped

        Returns:
            Path to the created action item, or None if creation failed
        """
        pass

    @abstractmethod
    def _generate_stable_id(self, file_path: Path) -> str:
        """Generate a stable identifier for deduplication.

        Args:
            file_path: Path to the file

        Returns:
            Stable identifier string
        """
        pass
