"""Read and parse Company Handbook rules for triage logic.

The handbook defines priority classification, communication tone,
permission boundaries, and output preferences.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def read_handbook_rules(vault_path: Path | str) -> Optional[Dict[str, str]]:
    """Read the Company Handbook and extract triage rules.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        Dictionary containing handbook rules, or None if handbook not found

    Example:
        >>> rules = read_handbook_rules("./AI_Employee_Vault")
        >>> print(rules['content'])
    """
    if isinstance(vault_path, str):
        vault_path = Path(vault_path)

    handbook_path = vault_path / "Company_Handbook.md"

    if not handbook_path.exists():
        logger.warning(f"Company Handbook not found: {handbook_path}")
        return None

    try:
        content = handbook_path.read_text(encoding="utf-8")

        rules = {
            "content": content,
            "path": str(handbook_path),
        }

        # Extract priority rules if present
        if "priority classification" in content.lower():
            rules["has_priority_rules"] = True

        # Extract permission boundaries if present
        if "permission boundaries" in content.lower():
            rules["has_permission_rules"] = True

        logger.info(f"Loaded handbook from: {handbook_path}")
        return rules

    except Exception as e:
        logger.error(
            f"Failed to read handbook {handbook_path}: {e}", exc_info=True
        )
        return None


def extract_priority_from_content(content: str, handbook_rules: Dict[str, str]) -> str:
    """Determine priority based on content and handbook rules.

    Args:
        content: Content to analyze for priority keywords
        handbook_rules: Rules from Company Handbook

    Returns:
        Priority level: "high", "medium", "low", or "auto"

    Example:
        >>> priority = extract_priority_from_content(
        ...     "URGENT: Need this done ASAP!",
        ...     handbook_rules
        ... )
        >>> print(priority)  # "high"
    """
    content_lower = content.lower()

    # High priority keywords (from typical handbook rules)
    high_keywords = [
        "urgent",
        "asap",
        "deadline",
        "payment",
        "security",
        "critical",
        "emergency",
    ]

    # Check for high priority indicators
    for keyword in high_keywords:
        if keyword in content_lower:
            return "high"

    # Low priority indicators
    low_keywords = ["newsletter", "fyi", "for your information", "optional"]

    for keyword in low_keywords:
        if keyword in content_lower:
            return "low"

    # Default to medium
    return "medium"
