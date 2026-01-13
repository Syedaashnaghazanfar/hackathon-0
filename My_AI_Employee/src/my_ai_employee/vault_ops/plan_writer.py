"""Create and write plan files for action items.

Plans contain actionable steps with checkboxes and a clear done condition.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import frontmatter

logger = logging.getLogger(__name__)


def create_plan(
    vault_path: Path | str,
    action_item_name: str,
    plan_content: str,
    source_item_path: Optional[Path] = None,
) -> Optional[Path]:
    """Create a plan file in the Plans folder.

    Args:
        vault_path: Path to the Obsidian vault root
        action_item_name: Name of the action item (for filename generation)
        plan_content: Content of the plan (should include checkboxes)
        source_item_path: Path to the source action item (for linking)

    Returns:
        Path to the created plan file, or None if creation failed

    Example:
        >>> plan_content = '''
        ... ## Action Items
        ... - [ ] Research vendors
        ... - [ ] Get quotes
        ... - [ ] Make decision
        ...
        ... ## Done Condition
        ... All checkboxes completed and vendor selected.
        ... '''
        >>> plan_path = create_plan(vault_path, "purchase_laptops", plan_content)
    """
    if isinstance(vault_path, str):
        vault_path = Path(vault_path)

    plans_dir = vault_path / "Plans"

    # Create Plans directory if it doesn't exist
    if not plans_dir.exists():
        logger.info(f"Creating Plans directory: {plans_dir}")
        plans_dir.mkdir(parents=True, exist_ok=True)

    # Generate plan filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = _sanitize_name(action_item_name)
    plan_filename = f"PLAN_{safe_name}_{timestamp}.md"
    plan_path = plans_dir / plan_filename

    try:
        # Create frontmatter
        metadata = {
            "type": "plan",
            "created": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }

        if source_item_path:
            metadata["source_item"] = str(source_item_path.name)

        # Build full content with header
        full_content = f"# Plan: {action_item_name}\n\n"

        if source_item_path:
            full_content += f"**Source**: [[{source_item_path.stem}]]\n\n"

        full_content += plan_content

        # Create and save Post
        post = frontmatter.Post(full_content, **metadata)
        plan_text = frontmatter.dumps(post)
        plan_path.write_text(plan_text, encoding="utf-8")

        logger.info(f"Created plan: {plan_path}")
        return plan_path

    except Exception as e:
        logger.error(f"Failed to create plan {plan_filename}: {e}", exc_info=True)
        return None


def _sanitize_name(name: str) -> str:
    """Sanitize a name for use in filenames.

    Args:
        name: Original name

    Returns:
        Sanitized name suitable for filenames
    """
    # Replace problematic characters
    sanitized = name.replace(" ", "_")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in ("_", "-"))

    # Limit length
    max_length = 50
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized or "plan"
