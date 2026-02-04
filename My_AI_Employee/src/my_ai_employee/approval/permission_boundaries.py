"""
Permission boundaries parser for Silver Tier AI Employee.

Parses auto-approve and require-approval rules from Company_Handbook.md.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from my_ai_employee.config import get_config


@dataclass
class PermissionBoundaries:
    """
    Permission boundaries configuration.

    Defines which actions can be auto-approved and which require human approval.
    """

    auto_approve_actions: List[str]
    require_approval_actions: List[str]
    exceptions: Dict[str, str]
    approval_criteria: List[str]

    def should_require_approval(self, action_type: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if an action requires human approval.

        Args:
            action_type: Type of action (send_email, publish_linkedin_post, vault_update, etc.)
            context: Additional context (e.g., recipient, content)

        Returns:
            True if approval required, False if auto-approve allowed

        Example:
            >>> boundaries = parse_permission_boundaries()
            >>> boundaries.should_require_approval("send_email")
            True
            >>> boundaries.should_require_approval("vault_update")
            False
        """
        # Normalize action type
        action_type_lower = action_type.lower()

        # Check if explicitly in auto-approve list
        for auto_action in self.auto_approve_actions:
            if auto_action.lower() in action_type_lower or action_type_lower in auto_action.lower():
                return False

        # Check if explicitly in require-approval list
        for req_action in self.require_approval_actions:
            if req_action.lower() in action_type_lower or action_type_lower in req_action.lower():
                return True

        # Check exceptions (e.g., pre-approved contacts)
        if context:
            for exception_key, exception_value in self.exceptions.items():
                if exception_key in context:
                    # If exception says "approve all" or similar, require approval
                    if "approve all" in exception_value.lower() or "always require" in exception_value.lower():
                        return True

        # Default: require approval for external actions
        external_action_keywords = ["send", "publish", "post", "execute", "payment", "form", "click"]
        for keyword in external_action_keywords:
            if keyword in action_type_lower:
                return True

        # Internal actions default to auto-approve
        return False


def parse_permission_boundaries(vault_path: Optional[Path] = None) -> PermissionBoundaries:
    """
    Parse permission boundaries from Company_Handbook.md.

    Args:
        vault_path: Path to vault root (defaults to config.vault_root)

    Returns:
        PermissionBoundaries instance

    Example:
        >>> boundaries = parse_permission_boundaries()
        >>> boundaries.auto_approve_actions
        ['Dashboard updates', 'vault operations', 'Reading emails']
    """
    if vault_path is None:
        config = get_config()
        vault_path = config.vault_root

    handbook_path = vault_path / "Company_Handbook.md"

    if not handbook_path.exists():
        # Return default boundaries if handbook not found
        return _default_boundaries()

    try:
        with open(handbook_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract sections
        auto_approve = _extract_section(content, "Auto-Approve Actions")
        require_approval = _extract_section(content, "Require-Approval Actions")
        exceptions = _extract_section(content, "Exceptions")
        criteria = _extract_section(content, "Approval Criteria")

        return PermissionBoundaries(
            auto_approve_actions=auto_approve,
            require_approval_actions=require_approval,
            exceptions=_parse_exceptions(exceptions),
            approval_criteria=criteria,
        )

    except Exception as e:
        print(f"Error parsing Company_Handbook.md: {e}")
        return _default_boundaries()


def _extract_section(content: str, section_name: str) -> List[str]:
    """
    Extract bullet points from a markdown section.

    Args:
        content: Markdown content
        section_name: Section heading name

    Returns:
        List of bullet points
    """
    items = []

    # Find section heading
    section_pattern = rf"###\s+{re.escape(section_name)}.*?\n(.*?)(?=###|\Z)"
    match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)

    if not match:
        return items

    section_content = match.group(1)

    # Extract bullet points
    bullet_pattern = r"^[\s]*[-*]\s+(.+)$"
    for line in section_content.split("\n"):
        bullet_match = re.match(bullet_pattern, line)
        if bullet_match:
            item = bullet_match.group(1).strip()
            # Remove markdown formatting
            item = re.sub(r"\*\*(.*?)\*\*", r"\1", item)  # Remove bold
            item = re.sub(r"\*(.*?)\*", r"\1", item)  # Remove italic
            items.append(item)

    return items


def _parse_exceptions(exception_items: List[str]) -> Dict[str, str]:
    """
    Parse exception items into key-value pairs.

    Args:
        exception_items: List of exception bullet points

    Returns:
        Dictionary of exceptions

    Example:
        >>> _parse_exceptions(["Emails to pre-approved contacts: none (approve all)"])
        {'emails_to_preapproved': 'none (approve all)'}
    """
    exceptions = {}

    for item in exception_items:
        # Split on first colon
        if ":" in item:
            key, value = item.split(":", 1)
            key = key.strip().lower().replace(" ", "_").replace("-", "_")
            value = value.strip()
            exceptions[key] = value

    return exceptions


def _default_boundaries() -> PermissionBoundaries:
    """
    Return default permission boundaries if Company_Handbook.md not found.

    Returns:
        Default PermissionBoundaries
    """
    return PermissionBoundaries(
        auto_approve_actions=[
            "Dashboard updates and vault operations",
            "Reading emails/messages (no sending)",
            "Internal triage and planning",
        ],
        require_approval_actions=[
            "Sending emails to ANY recipient",
            "Publishing LinkedIn posts",
            "Sending WhatsApp messages",
            "All browser automation (payments, form submissions, clicks)",
        ],
        exceptions={
            "emails_to_preapproved": "none (approve all by default)",
            "linkedin_posts": "always require approval",
            "financial_transactions": "always require approval with explicit amount confirmation",
        },
        approval_criteria=[
            "Recipient trust: Is the recipient a known, trusted contact?",
            "Content sensitivity: Does the message contain financial info, PII, or confidential data?",
            "Impact: What's the blast radius if this action fails or is misinterpreted?",
            "Reversibility: Can this action be easily undone or corrected?",
        ],
    )


def classify_action_risk(
    action_type: str,
    boundaries: PermissionBoundaries,
    context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Classify action risk level based on permission boundaries.

    Args:
        action_type: Type of action
        boundaries: Permission boundaries
        context: Additional context

    Returns:
        Risk level: "low", "medium", or "high"

    Example:
        >>> boundaries = parse_permission_boundaries()
        >>> classify_action_risk("send_email", boundaries)
        'high'
        >>> classify_action_risk("vault_update", boundaries)
        'low'
    """
    requires_approval = boundaries.should_require_approval(action_type, context)

    if not requires_approval:
        return "low"

    # Check for high-risk keywords
    high_risk_keywords = [
        "payment", "financial", "transaction", "delete", "remove",
        "linkedin", "post", "publish", "browser", "automation"
    ]

    action_lower = action_type.lower()
    for keyword in high_risk_keywords:
        if keyword in action_lower:
            return "high"

    # Medium risk for other external actions
    return "medium"
