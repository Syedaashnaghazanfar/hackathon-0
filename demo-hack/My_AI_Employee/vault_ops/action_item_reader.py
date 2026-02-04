"""
Action item reader for vault operations.

Reads pending action items from the Needs_Action folder for triage processing.
"""

from pathlib import Path
from typing import List, Tuple
import logging

from utils.frontmatter_utils import load_action_item, validate_action_item
import frontmatter


logger = logging.getLogger(__name__)


def read_pending_items(vault_path: str | Path) -> List[Tuple[Path, frontmatter.Post]]:
    """
    Read all pending action items from the Needs_Action folder.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        List of tuples (file_path, post) for each pending action item
        Returns empty list if no pending items or folder doesn't exist

    Raises:
        ValueError: If vault_path is invalid
    """
    vault_path = Path(vault_path)

    if not vault_path.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")

    needs_action_folder = vault_path / "Needs_Action"

    if not needs_action_folder.exists():
        logger.warning(f"Needs_Action folder not found: {needs_action_folder}")
        return []

    pending_items = []

    # Scan for markdown files in Needs_Action
    for item_file in needs_action_folder.glob("*.md"):
        try:
            # Load the action item
            post = load_action_item(item_file)

            # Validate the action item
            is_valid, error = validate_action_item(post)

            if not is_valid:
                logger.warning(f"Invalid action item {item_file.name}: {error}")
                # Still include invalid items so they can be handled by triage
                pending_items.append((item_file, post))
                continue

            # Check if status is pending
            if post.get('status') == 'pending':
                pending_items.append((item_file, post))
                logger.debug(f"Found pending item: {item_file.name}")
            else:
                logger.debug(f"Skipping non-pending item: {item_file.name} (status: {post.get('status')})")

        except Exception as e:
            logger.error(f"Error reading action item {item_file.name}: {e}")
            # Continue processing other items
            continue

    logger.info(f"Found {len(pending_items)} pending action items")
    return pending_items


def get_action_item_summary(post: frontmatter.Post) -> str:
    """
    Generate a brief summary of an action item for display.

    Args:
        post: Action item Post object

    Returns:
        Brief summary string (1-2 lines)
    """
    item_type = post.get('type', 'unknown')
    received = post.get('received', 'unknown')
    source = post.get('source_path', 'unknown')

    # Extract first line of content as title
    content_lines = post.content.strip().split('\n')
    title = content_lines[0].strip('#').strip() if content_lines else "Untitled"

    summary = f"{title} (type: {item_type}, received: {received[:10]})"

    return summary


def count_pending_items(vault_path: str | Path) -> int:
    """
    Count the number of pending action items in Needs_Action folder.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        Number of pending items
    """
    try:
        pending_items = read_pending_items(vault_path)
        return len(pending_items)
    except Exception as e:
        logger.error(f"Error counting pending items: {e}")
        return 0
