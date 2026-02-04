"""
Item archiver for vault operations.

Archives processed action items from Needs_Action/ to Done/ folder,
preserving all frontmatter metadata and adding processing information.
"""

from pathlib import Path
from datetime import datetime
import logging
import shutil

import frontmatter
from utils.frontmatter_utils import load_action_item, save_action_item


logger = logging.getLogger(__name__)


def archive_to_done(
    vault_path: str | Path,
    action_item_path: Path,
    result: str = "processed",
    related_plan_path: Path = None,
    additional_metadata: dict = None
) -> Path:
    """
    Archive an action item from Needs_Action/ to Done/ folder.

    Preserves all YAML frontmatter and adds processing metadata (FR-014).

    Args:
        vault_path: Path to the Obsidian vault root
        action_item_path: Path to the action item file to archive
        result: Result of processing (processed, planned, triaged, error)
        related_plan_path: Optional path to related plan file
        additional_metadata: Optional additional metadata to add

    Returns:
        Path to the archived file in Done/ folder

    Raises:
        ValueError: If paths are invalid
        IOError: If archiving fails
    """
    vault_path = Path(vault_path)
    action_item_path = Path(action_item_path)

    # Validate paths
    if not vault_path.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")

    if not action_item_path.exists():
        raise ValueError(f"Action item does not exist: {action_item_path}")

    done_folder = vault_path / "Done"

    if not done_folder.exists():
        logger.warning(f"Done folder not found, creating: {done_folder}")
        done_folder.mkdir(parents=True, exist_ok=True)

    try:
        # Load the action item (preserves all frontmatter)
        post = load_action_item(action_item_path)

        # Update status to processed
        post['status'] = 'processed'

        # Add processing timestamp
        post['processed'] = datetime.now().isoformat()

        # Add result
        post['result'] = result

        # Add related plan reference if provided
        if related_plan_path:
            post['related_plan'] = str(related_plan_path.name)

        # Add any additional metadata
        if additional_metadata:
            for key, value in additional_metadata.items():
                post[key] = value

        # Generate destination path in Done/ folder
        done_path = done_folder / action_item_path.name

        # Handle filename conflicts by appending timestamp
        if done_path.exists():
            stem = done_path.stem
            suffix = done_path.suffix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            done_path = done_folder / f"{stem}_{timestamp}{suffix}"
            logger.warning(f"File exists, using: {done_path.name}")

        # Save to Done/ folder (preserves all frontmatter)
        save_action_item(post, done_path)

        # Remove from Needs_Action/ folder
        action_item_path.unlink()

        logger.info(f"Archived {action_item_path.name} to Done/")
        return done_path

    except Exception as e:
        raise IOError(f"Failed to archive {action_item_path.name}: {e}")


def archive_multiple_items(
    vault_path: str | Path,
    action_item_paths: list[Path],
    result: str = "processed"
) -> list[Path]:
    """
    Archive multiple action items to Done/ folder.

    Args:
        vault_path: Path to the Obsidian vault root
        action_item_paths: List of action item paths to archive
        result: Result of processing

    Returns:
        List of archived file paths in Done/ folder
    """
    archived_paths = []

    for item_path in action_item_paths:
        try:
            archived_path = archive_to_done(vault_path, item_path, result=result)
            archived_paths.append(archived_path)
        except Exception as e:
            logger.error(f"Failed to archive {item_path.name}: {e}")
            # Continue with other items
            continue

    logger.info(f"Archived {len(archived_paths)}/{len(action_item_paths)} items")
    return archived_paths


def list_archived_items(vault_path: str | Path, limit: int = None) -> list[Path]:
    """
    List archived items in Done/ folder.

    Args:
        vault_path: Path to the Obsidian vault root
        limit: Optional limit on number of items to return (most recent first)

    Returns:
        List of archived item paths, sorted by modification time (newest first)
    """
    vault_path = Path(vault_path)
    done_folder = vault_path / "Done"

    if not done_folder.exists():
        logger.warning(f"Done folder not found: {done_folder}")
        return []

    # Get all markdown files
    archived_items = list(done_folder.glob("*.md"))

    # Sort by modification time (newest first)
    archived_items.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    # Apply limit if specified
    if limit:
        archived_items = archived_items[:limit]

    logger.info(f"Found {len(archived_items)} archived items")
    return archived_items


def get_archive_stats(vault_path: str | Path) -> dict:
    """
    Get statistics about archived items.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        Dictionary with archive statistics
    """
    archived_items = list_archived_items(vault_path)

    stats = {
        'total_archived': len(archived_items),
        'archive_folder': str(vault_path / "Done")
    }

    # Count by result type
    result_counts = {}
    for item_path in archived_items:
        try:
            post = load_action_item(item_path)
            result = post.get('result', 'unknown')
            result_counts[result] = result_counts.get(result, 0) + 1
        except Exception:
            continue

    stats['by_result'] = result_counts

    return stats
