"""Filesystem watcher that creates action items for dropped files.

Monitors a watch folder for new files and creates corresponding action items
in the Obsidian vault's Needs_Action folder with proper frontmatter metadata.
"""

import hashlib
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import frontmatter
from watchdog.events import FileSystemEvent
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

from ..utils import DedupeTracker, save_action_item
from .base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


class FilesystemWatcher(BaseWatcher):
    """Watches a folder for file drops and creates action items."""

    def __init__(
        self,
        vault_path: Path | str,
        watch_folder: Path | str,
        watch_mode: str = "events",
        dedupe_state_file: Optional[Path | str] = None,
    ):
        """Initialize the filesystem watcher.

        Args:
            vault_path: Path to the Obsidian vault root
            watch_folder: Path to the folder to watch for file drops
            watch_mode: Either "events" (default, uses native filesystem events)
                       or "polling" (fallback for WSL/network mounts)
            dedupe_state_file: Path to dedupe state file (default: .dedupe_state.json
                              in the project directory)
        """
        super().__init__(vault_path, watch_folder, watch_mode)

        # Ensure watch folder exists
        self.watch_folder.mkdir(parents=True, exist_ok=True)

        # Initialize deduplication tracker
        if dedupe_state_file is None:
            dedupe_state_file = Path.cwd() / ".dedupe_state.json"
        elif isinstance(dedupe_state_file, str):
            dedupe_state_file = Path(dedupe_state_file)

        self.dedupe_tracker = DedupeTracker(dedupe_state_file)

        logger.info(
            f"FilesystemWatcher initialized: "
            f"vault={self.vault_path}, "
            f"watch={self.watch_folder}, "
            f"mode={self.watch_mode}"
        )

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Args:
            event: Filesystem event from watchdog
        """
        # Ignore directory creation events
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Ignore temporary files and hidden files
        if file_path.name.startswith(".") or file_path.name.startswith("~"):
            logger.debug(f"Ignoring temporary/hidden file: {file_path}")
            return

        # Ignore common temporary file patterns
        temp_patterns = [".tmp", ".temp", ".swp", ".swo", "~"]
        if any(file_path.name.endswith(pattern) for pattern in temp_patterns):
            logger.debug(f"Ignoring temporary file: {file_path}")
            return

        logger.info(f"File created: {file_path}")

        try:
            # Generate stable ID for deduplication
            stable_id = self._generate_stable_id(file_path)

            # Check if already processed
            if self.dedupe_tracker.is_processed(stable_id):
                logger.info(f"File already processed (duplicate): {file_path}")
                return

            # Create action item
            action_item_path = self._create_action_item(file_path)

            if action_item_path:
                # Mark as processed
                self.dedupe_tracker.mark_processed(stable_id)
                logger.info(
                    f"Created action item: {action_item_path} for {file_path}"
                )
            else:
                logger.warning(f"Failed to create action item for: {file_path}")

        except Exception as e:
            # Log error but continue running (FR-008 resilience requirement)
            logger.error(
                f"Error processing file {file_path}: {e}", exc_info=True
            )

    def _create_action_item(self, file_path: Path) -> Optional[Path]:
        """Create an action item for a dropped file.

        Args:
            file_path: Path to the file that was dropped

        Returns:
            Path to the created action item, or None if creation failed
        """
        try:
            # Generate action item filename
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(file_path.name)
            action_item_name = f"FILE_{safe_filename}_{timestamp}.md"
            action_item_path = self.vault_path / "Needs_Action" / action_item_name

            # Get file stats for metadata
            stats = file_path.stat()
            file_size = stats.st_size

            # Create frontmatter metadata
            metadata = {
                "type": "file_drop",
                "received": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
                "priority": "auto",
                "source_id": self._generate_stable_id(file_path),
            }

            # Create content with reference to original file
            content = f"""# File Drop: {file_path.name}

## File Information
- **Original Path**: `{file_path.absolute()}`
- **File Size**: {self._format_file_size(file_size)}
- **Detected**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## Action Required
This file has been dropped into the watch folder. Review and determine next steps.
"""

            # Create frontmatter Post object
            post = frontmatter.Post(content, **metadata)

            # Save the action item
            save_action_item(action_item_path, post)

            return action_item_path

        except Exception as e:
            logger.error(
                f"Failed to create action item for {file_path}: {e}",
                exc_info=True,
            )
            return None

    def _generate_stable_id(self, file_path: Path) -> str:
        """Generate a stable identifier for deduplication.

        Uses file path, size, and modification time to create a unique ID.

        Args:
            file_path: Path to the file

        Returns:
            Stable identifier string (SHA256 hash)
        """
        try:
            stats = file_path.stat()
            # Combine path, size, and mtime for stable ID
            identifier = f"{file_path.absolute()}|{stats.st_size}|{stats.st_mtime}"
            return hashlib.sha256(identifier.encode()).hexdigest()
        except Exception as e:
            # Fallback to path-only hash if stat fails
            logger.warning(f"Could not stat file {file_path}, using path hash: {e}")
            return hashlib.sha256(str(file_path.absolute()).encode()).hexdigest()

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for use in action item names.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename suitable for markdown filenames
        """
        # Remove extension
        name_without_ext = Path(filename).stem

        # Replace problematic characters
        sanitized = name_without_ext.replace(" ", "_")
        sanitized = "".join(
            c for c in sanitized if c.isalnum() or c in ("_", "-")
        )

        # Limit length
        max_length = 50
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized or "file"

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.

        Args:
            size_bytes: File size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def run(self) -> None:
        """Start the watcher and run until interrupted.

        Uses either native filesystem events (Observer) or polling
        (PollingObserver) based on watch_mode configuration.
        """
        # Select observer based on watch mode
        if self.watch_mode == "polling":
            observer = PollingObserver()
            logger.info("Using PollingObserver (polling mode)")
        else:
            observer = Observer()
            logger.info("Using Observer (native events mode)")

        # Schedule the event handler
        observer.schedule(self, str(self.watch_folder), recursive=False)

        try:
            logger.info(f"Starting watcher on: {self.watch_folder}")
            observer.start()

            # Keep running until interrupted
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Watcher interrupted by user")
        except Exception as e:
            logger.error(f"Watcher error: {e}", exc_info=True)
        finally:
            logger.info("Stopping watcher...")
            observer.stop()
            observer.join()
            logger.info("Watcher stopped")
