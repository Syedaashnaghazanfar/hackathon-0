"""Deduplication state tracker for preventing duplicate action items.

Stores processed item IDs in a JSON file outside the vault to track
what has already been processed and prevent duplicate action items.
"""

import json
from pathlib import Path
from typing import Set


class DedupeTracker:
    """Tracks processed items to prevent duplicates.

    Uses a JSON file to store a set of processed item IDs. This file
    is stored outside the vault to avoid polluting user content.
    """

    def __init__(self, state_file: Path | str):
        """Initialize the dedupe tracker.

        Args:
            state_file: Path to the JSON file for storing processed IDs
        """
        if isinstance(state_file, str):
            state_file = Path(state_file)

        self.state_file = state_file
        self._processed_ids: Set[str] = set()
        self._load_state()

    def _load_state(self) -> None:
        """Load the dedupe state from disk if it exists."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._processed_ids = set(data.get("processed_ids", []))
            except (json.JSONDecodeError, OSError) as e:
                # If state file is corrupted, start fresh
                print(f"Warning: Could not load dedupe state: {e}")
                self._processed_ids = set()

    def _save_state(self) -> None:
        """Save the dedupe state to disk."""
        # Ensure parent directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"processed_ids": sorted(list(self._processed_ids))},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except OSError as e:
            print(f"Warning: Could not save dedupe state: {e}")

    def is_processed(self, item_id: str) -> bool:
        """Check if an item has already been processed.

        Args:
            item_id: Unique identifier for the item

        Returns:
            True if the item has been processed before, False otherwise
        """
        return item_id in self._processed_ids

    def mark_processed(self, item_id: str) -> None:
        """Mark an item as processed.

        Args:
            item_id: Unique identifier for the item
        """
        if item_id not in self._processed_ids:
            self._processed_ids.add(item_id)
            self._save_state()

    def clear(self) -> None:
        """Clear all processed IDs (use with caution)."""
        self._processed_ids.clear()
        self._save_state()

    def count(self) -> int:
        """Return the number of processed items."""
        return len(self._processed_ids)
