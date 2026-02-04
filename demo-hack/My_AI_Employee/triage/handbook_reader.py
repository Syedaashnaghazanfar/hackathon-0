"""
Handbook reader for triage operations.

Reads and parses Company_Handbook.md to extract processing rules
and guidelines for action item triage.
"""

from pathlib import Path
import logging


logger = logging.getLogger(__name__)


def read_handbook_rules(vault_path: str | Path) -> str:
    """
    Read the Company Handbook and extract processing rules.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        Content of Company_Handbook.md as string
        Returns empty string if handbook doesn't exist

    Raises:
        ValueError: If vault_path is invalid
    """
    vault_path = Path(vault_path)

    if not vault_path.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")

    handbook_path = vault_path / "Company_Handbook.md"

    if not handbook_path.exists():
        logger.warning(f"Company Handbook not found: {handbook_path}")
        return ""

    try:
        content = handbook_path.read_text(encoding='utf-8')
        logger.info(f"Read Company Handbook ({len(content)} characters)")
        return content
    except Exception as e:
        logger.error(f"Failed to read Company Handbook: {e}")
        return ""


def extract_priority_rules(handbook_content: str) -> dict:
    """
    Extract priority classification rules from handbook content.

    Args:
        handbook_content: Content of Company_Handbook.md

    Returns:
        Dictionary with priority rules and keywords
    """
    # Simple keyword-based priority extraction
    # In a real implementation, this could use more sophisticated parsing

    priority_rules = {
        'high': [],
        'medium': [],
        'low': []
    }

    # Look for priority-related sections
    lines = handbook_content.lower().split('\n')

    current_priority = None
    for line in lines:
        if 'high priority' in line or 'urgent' in line:
            current_priority = 'high'
        elif 'medium priority' in line or 'normal' in line:
            current_priority = 'medium'
        elif 'low priority' in line or 'routine' in line:
            current_priority = 'low'

        # Extract keywords if we're in a priority section
        if current_priority and ('keyword' in line or 'indicator' in line):
            # Extract words in quotes or after colons
            words = line.split(':')[-1].strip()
            if words:
                priority_rules[current_priority].append(words)

    return priority_rules


def extract_permission_boundaries(handbook_content: str) -> list[str]:
    """
    Extract permission boundaries from handbook content.

    Args:
        handbook_content: Content of Company_Handbook.md

    Returns:
        List of permission boundary statements
    """
    boundaries = []

    lines = handbook_content.split('\n')

    in_permissions_section = False
    for line in lines:
        line_lower = line.lower()

        # Detect permissions section
        if 'permission' in line_lower or 'boundary' in line_lower or 'allowed' in line_lower:
            in_permissions_section = True

        # Extract boundary statements
        if in_permissions_section:
            if line.strip().startswith('-') or line.strip().startswith('*'):
                boundaries.append(line.strip().lstrip('-*').strip())

        # Exit section on blank line or new heading
        if in_permissions_section and (not line.strip() or line.startswith('#')):
            if boundaries:  # Only exit if we've collected some boundaries
                in_permissions_section = False

    return boundaries


def get_handbook_summary(vault_path: str | Path) -> dict:
    """
    Get a summary of handbook rules and guidelines.

    Args:
        vault_path: Path to the Obsidian vault root

    Returns:
        Dictionary with handbook summary information
    """
    handbook_content = read_handbook_rules(vault_path)

    if not handbook_content:
        return {
            'exists': False,
            'content_length': 0,
            'priority_rules': {},
            'permission_boundaries': []
        }

    priority_rules = extract_priority_rules(handbook_content)
    permission_boundaries = extract_permission_boundaries(handbook_content)

    return {
        'exists': True,
        'content_length': len(handbook_content),
        'priority_rules': priority_rules,
        'permission_boundaries': permission_boundaries,
        'full_content': handbook_content
    }


def check_handbook_compliance(action_description: str, handbook_content: str) -> dict:
    """
    Check if a proposed action complies with handbook rules.

    Args:
        action_description: Description of the proposed action
        handbook_content: Content of Company_Handbook.md

    Returns:
        Dictionary with compliance check results
    """
    action_lower = action_description.lower()
    handbook_lower = handbook_content.lower()

    # Check for prohibited actions
    prohibited_keywords = [
        'external api', 'send email', 'make payment', 'delete production',
        'deploy to production', 'access external service'
    ]

    violations = []
    for keyword in prohibited_keywords:
        if keyword in action_lower and 'no ' + keyword in handbook_lower:
            violations.append(f"Action may violate handbook: '{keyword}' appears to be prohibited")

    # Check for required approvals
    requires_approval = False
    if any(word in action_lower for word in ['delete', 'remove', 'drop', 'destroy']):
        requires_approval = True

    return {
        'compliant': len(violations) == 0,
        'violations': violations,
        'requires_approval': requires_approval,
        'recommendation': 'Proceed' if len(violations) == 0 else 'Review required'
    }
