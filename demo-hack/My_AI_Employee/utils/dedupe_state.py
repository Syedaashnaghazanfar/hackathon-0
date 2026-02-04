"""
Dedupe state tracker for preventing duplicate action items.

Tracks processed files using stable IDs to prevent the watcher
from creating duplicate action items for the same file.
"""

import json
import hashlib
from pathlib import Path
from typing import Set, Optional
from datetime import datetime


class DedupeTracker:
    """
    Tracks processed file IDs to prevent duplicate action items.

    State is stored in a JSON file outside the vault to avoid
    polluting the Obsidian vault with system files.
    """

    def __init__(self, state_file: str | Path = "dedupe_state.json"):
        """
        Initialize dedupe tracker.

        Args:
            state_file: Path to JSON file storing processed IDs
                       (relative to project root or absolute)
        """
        self.state_file = Path(state_file)
        self.processed_ids: Set[str] = set()
        self._load_state()

    def _load_state(self) -> None:
        """Load processed IDs from state file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_ids = set(data.get('processed_ids', []))
            except (json.JSONDecodeError, IOError) as e:
                # If state file is corrupted, start fresh
                print(f"Warning: Could not load dedupe state: {e}")
                self.processed_ids = set()

    def _save_state(self) -> None:
        """Save processed IDs to state file."""
        try:
            # Ensure parent directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'processed_ids': list(self.processed_ids),
                'last_updated': datetime.now().isoformat(),
                'count': len(self.processed_ids)
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save dedupe state: {e}")

    def generate_file_id(self, file_path: str | Path) -> str:
        """
        Generate a stable ID for a file based on path and metadata.

        Args:
            file_path: Path to the file

        Returns:
            Stable ID string (SHA256 hash)
        """
        file_path = Path(file_path).resolve()

        # Use absolute path as primary identifier
        path_str = str(file_path)

        # Add file size and mtime if file exists
        if file_path.exists():
            stat = file_path.stat()
            path_str += f"|{stat.st_size}|{stat.st_mtime}"

        # Generate SHA256 hash
        file_id = hashlib.sha256(path_str.encode('utf-8')).hexdigest()

        return file_id

    def is_processed(self, file_id: str) -> bool:
        """
        Check if a file ID has been processed.

        Args:
            file_id: File ID to check

        Returns:
            True if already processed, False otherwise
        """
        return file_id in self.processed_ids

    def mark_processed(self, file_id: str) -> None:
        """
        Mark a file ID as processed.

        Args:
            file_id: File ID to mark as processed
        """
        self.processed_ids.add(file_id)
        self._save_state()

    def is_file_processed(self, file_path: str | Path) -> bool:
        """
        Check if a file has been processed (convenience method).

        Args:
            file_path: Path to the file

        Returns:
            True if already processed, False otherwise
        """
        file_id = self.generate_file_id(file_path)
        return self.is_processed(file_id)

    def mark_file_processed(self, file_path: str | Path) -> str:
        """
        Mark a file as processed (convenience method).

        Args:
            file_path: Path to the file

        Returns:
            The generated file ID
        """
        file_id = self.generate_file_id(file_path)
        self.mark_processed(file_id)
        return file_id

    def clear(self) -> None:
        """Clear all processed IDs (use with caution)."""
        self.processed_ids.clear()
        self._save_state()

    def get_stats(self) -> dict:
        """
        Get statistics about processed files.

        Returns:
            Dictionary with stats (count, state_file_path)
        """
        return {
            'processed_count': len(self.processed_ids),
            'state_file': str(self.state_file.resolve()),
            'state_file_exists': self.state_file.exists()
        }
