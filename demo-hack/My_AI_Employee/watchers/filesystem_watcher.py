"""
Filesystem watcher for monitoring a drop folder and creating action items.

Watches a specified folder for new files and creates corresponding action items
in the Obsidian vault's Needs_Action folder with proper frontmatter.
"""

import time
from pathlib import Path
from datetime import datetime
from typing import Optional
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEvent

from watchers.base_watcher import BaseWatcher
from utils.dedupe_state import DedupeTracker
from utils.frontmatter_utils import create_action_item, save_action_item


class FilesystemWatcher(BaseWatcher):
    """
    Watches a filesystem folder for new files and creates action items.

    When a new file is detected, creates a markdown action item in the
    vault's Needs_Action folder with proper frontmatter metadata.
    """

    def __init__(
        self,
        vault_path: str | Path,
        watch_folder: str | Path,
        watch_mode: str = "events",
        check_interval: int = 60
    ):
        """
        Initialize filesystem watcher.

        Args:
            vault_path: Path to Obsidian vault root
            watch_folder: Path to folder to watch for new files
            watch_mode: "events" for native events, "polling" for polling mode
            check_interval: Seconds between checks (for polling mode)
        """
        super().__init__(vault_path, check_interval)

        self.watch_folder = Path(watch_folder)
        self.watch_mode = watch_mode.lower()

        # Initialize dedupe tracker (stored outside vault)
        self.dedupe_tracker = DedupeTracker("dedupe_state.json")

        # Validate paths
        if not self.watch_folder.exists():
            raise ValueError(f"Watch folder does not exist: {self.watch_folder}")

        if not self.validate_vault_structure():
            raise ValueError(f"Invalid vault structure at: {self.vault_path}")

        self.logger.info(f"FilesystemWatcher initialized")
        self.logger.info(f"  Vault: {self.vault_path}")
        self.logger.info(f"  Watch folder: {self.watch_folder}")
        self.logger.info(f"  Watch mode: {self.watch_mode}")

    def _generate_stable_id(self, file_path: Path) -> str:
        """
        Generate a stable ID for a file to prevent duplicates.

        Uses the DedupeTracker to generate a hash based on file path,
        size, and modification time.

        Args:
            file_path: Path to the file

        Returns:
            Stable ID string (SHA256 hash)
        """
        return self.dedupe_tracker.generate_file_id(file_path)

    def _create_action_item(self, file_path: Path) -> Optional[Path]:
        """
        Create an action item markdown file in Needs_Action folder.

        Args:
            file_path: Path to the file that triggered the action

        Returns:
            Path to created action item, or None if creation failed
        """
        try:
            # Generate stable ID for deduplication
            file_id = self._generate_stable_id(file_path)

            # Check if already processed
            if self.dedupe_tracker.is_processed(file_id):
                self.logger.info(f"File already processed (duplicate): {file_path.name}")
                return None

            # Generate action item filename with microseconds for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            safe_filename = file_path.stem.replace(" ", "_")[:50]  # Limit length
            action_filename = f"{timestamp}_{safe_filename}.md"
            action_path = self.needs_action / action_filename

            # Create action item content
            content = f"""# Action Required: {file_path.name}

## Source File
- **Path**: `{file_path.resolve()}`
- **Size**: {file_path.stat().st_size} bytes
- **Modified**: {datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()}

## Description
New file detected in watch folder. Review and determine appropriate action.

## Next Steps
- [ ] Review file contents
- [ ] Determine priority and category
- [ ] Create plan if needed
- [ ] Archive to Done when complete
"""

            # Create frontmatter Post object
            post = create_action_item(
                content=content,
                item_type="file_drop",
                status="pending",
                source_path=str(file_path.resolve()),
                file_id=file_id,
                detected=datetime.now().isoformat()
            )

            # Save action item
            save_action_item(post, action_path)

            # Mark as processed in dedupe tracker
            self.dedupe_tracker.mark_processed(file_id)

            self.logger.info(f"Created action item: {action_path.name}")
            return action_path

        except Exception as e:
            self.logger.error(f"Failed to create action item for {file_path}: {e}")
            return None

    def on_created(self, event: FileSystemEvent) -> None:
        """
        Handle file creation events.

        Called by watchdog when a new file is created in the watched folder.

        Args:
            event: FileSystemEvent object from watchdog
        """
        # Ignore directory creation
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        self.logger.info(f"File created: {file_path.name}")

        try:
            # Create action item for the new file
            action_path = self._create_action_item(file_path)

            if action_path:
                self.logger.info(f"Successfully processed: {file_path.name}")
            else:
                self.logger.debug(f"Skipped (duplicate or error): {file_path.name}")

        except Exception as e:
            # Log error but continue running (FR-008: resilience)
            self.logger.error(f"Error processing {file_path.name}: {e}", exc_info=True)

    def check_for_updates(self) -> list:
        """
        Check for new files in watch folder (for polling mode).

        Returns:
            List of new file paths to process
        """
        try:
            new_files = []

            # Scan watch folder for files
            for file_path in self.watch_folder.iterdir():
                if file_path.is_file():
                    file_id = self._generate_stable_id(file_path)

                    # Check if not yet processed
                    if not self.dedupe_tracker.is_processed(file_id):
                        new_files.append(file_path)

            return new_files

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return []

    def create_action_file(self, item) -> Optional[Path]:
        """
        Create action file for an item (required by BaseWatcher).

        Args:
            item: File path to process

        Returns:
            Path to created action item, or None if failed
        """
        if isinstance(item, (str, Path)):
            return self._create_action_item(Path(item))
        return None

    def run(self) -> None:
        """
        Start the watcher and run until interrupted.

        Uses Observer for native filesystem events (default) or
        PollingObserver as fallback for WSL/network filesystems.
        """
        self.logger.info("Starting filesystem watcher...")

        # Choose observer based on watch_mode
        if self.watch_mode == "polling":
            observer = PollingObserver(timeout=self.check_interval)
            self.logger.info("Using PollingObserver (polling mode)")
        else:
            observer = Observer()
            self.logger.info("Using Observer (native events)")

        try:
            # Schedule the event handler
            observer.schedule(
                self,
                str(self.watch_folder),
                recursive=False
            )

            # Start observer
            observer.start()
            self.logger.info(f"Watching folder: {self.watch_folder}")
            self.logger.info("Press Ctrl+C to stop")

            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Stopping watcher...")
                observer.stop()

            # Wait for observer to finish
            observer.join()
            self.logger.info("Watcher stopped")

        except Exception as e:
            self.logger.error(f"Fatal error in watcher: {e}", exc_info=True)
            raise
