"""Read action items from the vault's Needs_Action folder.

Provides functionality to scan and load pending action items for triage processing.
"""

import logging
from pathlib import Path
from typing import List, Tuple

import frontmatter

from ..utils import load_action_item

logger = logging.getLogger(__name__)


def read_pending_items(vault_path: Path | str) -> List[Tuple[Path, frontmatter.Post]]:
    """Read all pending action items from Needs_Action folder.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        List of tuples containing (file_path, frontmatter.Post) for each item

    Example:
        >>> items = read_pending_items("./AI_Employee_Vault")
        >>> for path, post in items:
        ...     print(f"Processing: {post['type']} from {path.name}")
    """
    if isinstance(vault_path, str):
        vault_path = Path(vault_path)

    needs_action_dir = vault_path / "Needs_Action"

    if not needs_action_dir.exists():
        logger.warning(f"Needs_Action folder not found: {needs_action_dir}")
        return []

    pending_items = []

    # Scan for markdown files
    for item_file in needs_action_dir.glob("*.md"):
        try:
            post = load_action_item(item_file)

            # Only include items with status=pending
            if post.get("status") == "pending":
                pending_items.append((item_file, post))
                logger.debug(f"Loaded pending item: {item_file.name}")
            else:
                logger.debug(
                    f"Skipping non-pending item: {item_file.name} (status={post.get('status')})"
                )

        except Exception as e:
            logger.error(
                f"Failed to load action item {item_file}: {e}", exc_info=True
            )
            # Add to pending items with error marker for triage to handle
            try:
                post = frontmatter.load(str(item_file))
                post["_load_error"] = str(e)
                pending_items.append((item_file, post))
            except Exception:
                # If even basic loading fails, skip this item
                logger.error(f"Could not load malformed item: {item_file}")

    logger.info(f"Found {len(pending_items)} pending items in Needs_Action")
    return pending_items
