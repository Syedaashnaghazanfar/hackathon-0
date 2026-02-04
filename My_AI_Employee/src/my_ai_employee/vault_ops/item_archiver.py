"""Archive processed action items to the Done folder.

Per FR-014: Must preserve YAML frontmatter when archiving.

Silver Tier Extension: Support moving items between approval workflow folders
(Pending_Approval, Approved, Rejected, Failed).
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..utils import load_action_item, save_action_item

logger = logging.getLogger(__name__)


def archive_to_done(
    vault_path: Path | str,
    item_path: Path,
    result: str = "processed",
    related_plan_path: Optional[Path] = None,
) -> Optional[Path]:
    """Archive an action item to the Done folder.

    Preserves all existing YAML frontmatter and adds processing metadata:
    - status: processed
    - processed: <ISO timestamp>
    - result: planned|triaged|error
    - related_plan: <path> (if applicable)

    Args:
        vault_path: Path to the Obsidian vault root
        item_path: Path to the action item to archive
        result: Processing result (planned|triaged|error)
        related_plan_path: Path to related plan file, if any

    Returns:
        Path to the archived file in Done/, or None if archiving failed

    Example:
        >>> archived_path = archive_to_done(
        ...     vault_path="./AI_Employee_Vault",
        ...     item_path=Path("./AI_Employee_Vault/Needs_Action/item.md"),
        ...     result="planned",
        ...     related_plan_path=Path("./AI_Employee_Vault/Plans/plan.md")
        ... )
    """
    if isinstance(vault_path, str):
        vault_path = Path(vault_path)

    done_dir = vault_path / "Done"

    # Ensure Done directory exists
    if not done_dir.exists():
        logger.info(f"Creating Done directory: {done_dir}")
        done_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load the action item (preserves frontmatter)
        post = load_action_item(item_path)

        # Add processing metadata
        post["status"] = "processed"
        post["processed"] = datetime.now(timezone.utc).isoformat()
        post["result"] = result

        if related_plan_path:
            post["related_plan"] = str(related_plan_path.name)

        # Determine archive filename (same name as original)
        archive_path = done_dir / item_path.name

        # Handle filename conflicts by appending timestamp
        if archive_path.exists():
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            name_stem = archive_path.stem
            archive_path = done_dir / f"{name_stem}_{timestamp}.md"
            logger.debug(f"Filename conflict resolved: {archive_path.name}")

        # Save to Done folder
        save_action_item(archive_path, post)

        # Remove from Needs_Action
        item_path.unlink()

        logger.info(f"Archived: {item_path.name} → Done/{archive_path.name}")
        return archive_path

    except Exception as e:
        logger.error(
            f"Failed to archive {item_path.name}: {e}", exc_info=True
        )
        return None


# Silver Tier Functions

def move_item_between_folders(
    vault_path: Path | str,
    item_path: Path,
    destination_folder: str,
    preserve_frontmatter: bool = True,
) -> Optional[Path]:
    """
    Move an item between vault folders (Silver tier approval workflow).

    Args:
        vault_path: Path to the Obsidian vault root
        item_path: Path to the item to move
        destination_folder: Destination folder name (Pending_Approval, Approved, Rejected, Failed, Done)
        preserve_frontmatter: Whether to preserve existing frontmatter (default: True)

    Returns:
        Path to the moved file, or None if move failed

    Example:
        >>> # Approve an action (move from Pending_Approval to Approved)
        >>> moved_path = move_item_between_folders(
        ...     vault_path="./AI_Employee_Vault",
        ...     item_path=Path("./AI_Employee_Vault/Pending_Approval/action.md"),
        ...     destination_folder="Approved"
        ... )
    """
    if isinstance(vault_path, str):
        vault_path = Path(vault_path)

    dest_dir = vault_path / destination_folder

    # Ensure destination directory exists
    if not dest_dir.exists():
        logger.info(f"Creating destination directory: {dest_dir}")
        dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        if preserve_frontmatter:
            # Load with frontmatter preservation
            post = load_action_item(item_path)

            # Determine destination filename (same name as original)
            dest_path = dest_dir / item_path.name

            # Handle filename conflicts
            if dest_path.exists():
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                name_stem = dest_path.stem
                dest_path = dest_dir / f"{name_stem}_{timestamp}.md"
                logger.debug(f"Filename conflict resolved: {dest_path.name}")

            # Save to destination
            save_action_item(dest_path, post)

            # Remove from source
            item_path.unlink()

            logger.info(f"Moved: {item_path.name} → {destination_folder}/{dest_path.name}")
            return dest_path

        else:
            # Simple move without frontmatter parsing
            dest_path = dest_dir / item_path.name

            if dest_path.exists():
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                name_stem = dest_path.stem
                dest_path = dest_dir / f"{name_stem}_{timestamp}.md"

            item_path.rename(dest_path)
            logger.info(f"Moved: {item_path.name} → {destination_folder}/{dest_path.name}")
            return dest_path

    except Exception as e:
        logger.error(
            f"Failed to move {item_path.name} to {destination_folder}: {e}", exc_info=True
        )
        return None
