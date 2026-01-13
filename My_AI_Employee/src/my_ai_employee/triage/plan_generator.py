"""Generate plan content for action items.

Creates plans with checkboxes, done conditions, and actionable steps.
"""

import logging
from typing import Dict

import frontmatter

logger = logging.getLogger(__name__)


def generate_plan_content(action_item: frontmatter.Post, handbook_rules: Dict[str, str]) -> str:
    """Generate a plan with checkboxes and done condition for an action item.

    Args:
        action_item: The action item Post object
        handbook_rules: Rules from Company Handbook

    Returns:
        Plan content as markdown string

    Example:
        >>> plan = generate_plan_content(action_item, handbook_rules)
        >>> assert "- [ ]" in plan  # Has checkboxes
        >>> assert "Done Condition" in plan  # Has done condition
    """
    item_type = action_item.get("type", "unknown")
    item_content = action_item.content
    priority = action_item.get("priority", "auto")

    # Build plan content
    plan_parts = []

    # Summary section
    plan_parts.append("## Summary")
    plan_parts.append(f"**Type**: {item_type}")
    plan_parts.append(f"**Priority**: {priority}")
    plan_parts.append("")

    # Action items section with checkboxes
    plan_parts.append("## Action Items")

    # Generate context-appropriate steps based on type
    if item_type == "file_drop":
        plan_parts.append("- [ ] Review the dropped file content")
        plan_parts.append("- [ ] Determine appropriate action")
        plan_parts.append("- [ ] Execute or delegate the task")
        plan_parts.append("- [ ] Confirm completion")
    elif item_type == "email":
        plan_parts.append("- [ ] Read and understand the email request")
        plan_parts.append("- [ ] Draft response or action plan")
        plan_parts.append("- [ ] Get necessary approvals if required")
        plan_parts.append("- [ ] Send response or complete action")
    else:
        # Generic plan for manual or unknown types
        plan_parts.append("- [ ] Analyze the request")
        plan_parts.append("- [ ] Break down into sub-tasks if needed")
        plan_parts.append("- [ ] Complete each sub-task")
        plan_parts.append("- [ ] Verify outcome meets requirements")

    plan_parts.append("")

    # Context section (excerpt from original item)
    plan_parts.append("## Context")
    # Include first 200 characters of content
    excerpt = item_content[:200].strip()
    if len(item_content) > 200:
        excerpt += "..."
    plan_parts.append(f"> {excerpt}")
    plan_parts.append("")

    # Permission boundaries reminder (Bronze tier)
    plan_parts.append("## Constraints")
    plan_parts.append("**Bronze Tier Limitations**:")
    plan_parts.append("- No external actions (no emails, social posts, payments)")
    plan_parts.append("- Create drafts and plans only")
    plan_parts.append("- Human review required for all actions")
    plan_parts.append("")

    # Done condition
    plan_parts.append("## Done Condition")
    plan_parts.append("This item is complete when:")
    plan_parts.append("- All checkboxes above are marked [X]")
    plan_parts.append("- Output/result is documented")
    plan_parts.append("- Human has reviewed and approved")
    plan_parts.append("")

    return "\n".join(plan_parts)


def is_malformed_item(action_item: frontmatter.Post) -> bool:
    """Check if an action item is malformed.

    Per FR-015: Malformed items should remain in Needs_Action with dashboard warning.

    Args:
        action_item: The action item Post object

    Returns:
        True if item is malformed, False otherwise
    """
    # Check for load errors
    if "_load_error" in action_item.metadata:
        logger.warning(f"Item has load error: {action_item.get('_load_error')}")
        return True

    # Check required fields
    required_fields = ["type", "received", "status"]
    for field in required_fields:
        if field not in action_item.metadata:
            logger.warning(f"Item missing required field: {field}")
            return True

    # Check type validity
    valid_types = ["file_drop", "email", "manual"]
    if action_item.get("type") not in valid_types:
        logger.warning(f"Invalid type: {action_item.get('type')}")
        return True

    return False
