"""Shared utilities for AI Employee."""

from .frontmatter_utils import load_action_item, save_action_item
from .dedupe_state import DedupeTracker

__all__ = ["load_action_item", "save_action_item", "DedupeTracker"]
