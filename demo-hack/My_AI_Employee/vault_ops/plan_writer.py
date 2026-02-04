"""
Plan writer for vault operations.

Creates plan files in the Plans/ folder based on action items and triage decisions.
"""

from pathlib import Path
from datetime import datetime
import logging

import frontmatter


logger = logging.getLogger(__name__)


def create_plan(
    vault_path: str | Path,
    action_item_name: str,
    plan_content: str,
    metadata: dict = None
) -> Path:
    """
    Create a plan file in the Plans/ folder.

    Args:
        vault_path: Path to the Obsidian vault root
        action_item_name: Name of the action item this plan is for
        plan_content: Markdown content for the plan
        metadata: Optional metadata to include in frontmatter

    Returns:
        Path to the created plan file

    Raises:
        ValueError: If vault_path is invalid
        IOError: If plan file cannot be created
    """
    vault_path = Path(vault_path)

    if not vault_path.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")

    plans_folder = vault_path / "Plans"

    if not plans_folder.exists():
        logger.warning(f"Plans folder not found, creating: {plans_folder}")
        plans_folder.mkdir(parents=True, exist_ok=True)

    # Generate plan filename based on action item name
    # Remove timestamp prefix if present
    base_name = action_item_name.replace('.md', '')

    # Try to extract meaningful name after timestamp
    parts = base_name.split('_', 3)
    if len(parts) >= 4:
        # Format: YYYYMMDD_HHMMSS_microseconds_name
        meaningful_name = parts[3]
    else:
        meaningful_name = base_name

    plan_filename = f"Plan_{meaningful_name}.md"
    plan_path = plans_folder / plan_filename

    # Prepare frontmatter
    plan_metadata = {
        'created': datetime.now().isoformat(),
        'source_action_item': action_item_name,
        'status': 'active'
    }

    # Add custom metadata if provided
    if metadata:
        plan_metadata.update(metadata)

    # Create frontmatter Post object
    post = frontmatter.Post(plan_content, **plan_metadata)

    # Save plan file
    try:
        # Serialize to string first, then write
        content = frontmatter.dumps(post)
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created plan: {plan_path.name}")
        return plan_path

    except Exception as e:
        raise IOError(f"Failed to create plan file {plan_path}: {e}")


def generate_plan_template(
    action_item_post: frontmatter.Post,
    handbook_rules: str = None
) -> str:
    """
    Generate a plan template based on an action item.

    Args:
        action_item_post: The action item Post object
        handbook_rules: Optional handbook rules to consider

    Returns:
        Markdown content for the plan
    """
    # Extract action item details
    item_type = action_item_post.get('type', 'unknown')
    source_path = action_item_post.get('source_path', 'N/A')

    # Extract title from content
    content_lines = action_item_post.content.strip().split('\n')
    title = content_lines[0].strip('#').strip() if content_lines else "Untitled Action"

    # Generate plan content
    plan_content = f"""# Plan: {title}

## Action Item Details
- **Type**: {item_type}
- **Source**: {source_path}
- **Received**: {action_item_post.get('received', 'unknown')}

## Analysis
<!-- Add analysis of the action item here -->

## Proposed Actions
<!-- List specific actions to take -->

- [ ] Action 1
- [ ] Action 2
- [ ] Action 3

## Done Condition
<!-- Describe when this plan is considered complete -->

This plan is complete when:
- All action items are checked off
- Results are documented
- Source item is archived to Done/

## Notes
<!-- Add any additional notes or considerations -->
"""

    if handbook_rules:
        plan_content += f"\n## Handbook Guidance\n{handbook_rules}\n"

    return plan_content


def list_plans(vault_path: str | Path) -> list[Path]:
    """
    List all plan files in the Plans/ folder.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        List of plan file paths
    """
    vault_path = Path(vault_path)
    plans_folder = vault_path / "Plans"

    if not plans_folder.exists():
        logger.warning(f"Plans folder not found: {plans_folder}")
        return []

    plans = list(plans_folder.glob("*.md"))
    logger.info(f"Found {len(plans)} plans")
    return plans
