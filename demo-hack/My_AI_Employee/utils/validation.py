"""
Validation utilities for Silver Tier AI Employee.

Provides validation functions for approval requests, action items,
and other data structures to ensure they conform to expected schemas
before processing.
"""

import frontmatter
from pathlib import Path
from typing import Optional, Dict, Any
from models.schemas import ApprovalRequest, ActionItem, Priority, RiskLevel, Status, ActionType, MCPServer


def validate_approval_request_file(file_path: Path) -> tuple[bool, Optional[ApprovalRequest], list[str]]:
    """
    Validate an approval request file.

    Args:
        file_path: Path to the approval request markdown file

    Returns:
        Tuple of (is_valid, approval_request, errors)
        - is_valid: True if file is valid
        - approval_request: Parsed ApprovalRequest object if valid, None otherwise
        - errors: List of validation error messages
    """
    errors = []

    try:
        # Read file with frontmatter
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        metadata = post.metadata

        # Check required fields
        required_fields = ['action_type', 'mcp_server', 'priority', 'risk_level', 'status']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, None, errors

        # Validate with Pydantic
        try:
            approval = ApprovalRequest(**metadata)
            return True, approval, []
        except Exception as e:
            errors.append(f"Pydantic validation failed: {str(e)}")
            return False, None, errors

    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
        return False, None, errors


def extract_email_details_from_body(content: str) -> Dict[str, str]:
    """
    Extract email details from approval request body.

    Looks for patterns like:
    **To:** email@example.com
    **Subject:** Email subject

    Args:
        content: Markdown content of approval request

    Returns:
        Dict with 'to', 'subject', 'body' keys
    """
    import re

    details = {}

    # Extract To
    to_match = re.search(r'\*\*To:\*\*\s*(.+)', content)
    if to_match:
        details['to'] = to_match.group(1).strip()

    # Extract Subject
    subject_match = re.search(r'\*\*Subject:\*\*\s*(.+)', content)
    if subject_match:
        details['subject'] = subject_match.group(1).strip()

    # Extract Body (everything after ## Body heading)
    body_match = re.search(r'##\s*Body\s*\n\n(.+)', content, re.DOTALL)
    if body_match:
        details['body'] = body_match.group(1).strip()

    return details


def create_approval_request_markdown(approval: ApprovalRequest) -> str:
    """
    Create properly formatted approval request markdown.

    Uses the ApprovalRequest Pydantic model to generate
    a markdown file that conforms to mcp-executor spec.

    Args:
        approval: ApprovalRequest Pydantic model

    Returns:
        Formatted markdown string
    """
    return approval.to_markdown()


def validate_action_item_file(file_path: Path) -> tuple[bool, Optional[ActionItem], list[str]]:
    """
    Validate an action item file.

    Args:
        file_path: Path to the action item markdown file

    Returns:
        Tuple of (is_valid, action_item, errors)
    """
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        metadata = post.metadata

        # Check required fields
        required_fields = ['action_type', 'type', 'priority', 'risk_level', 'received', 'sender', 'subject', 'body']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, None, errors

        # Validate with Pydantic
        try:
            action_item = ActionItem(**metadata)
            return True, action_item, []
        except Exception as e:
            errors.append(f"Pydantic validation failed: {str(e)}")
            return False, None, errors

    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
        return False, None, errors
