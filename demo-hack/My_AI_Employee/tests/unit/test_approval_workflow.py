"""
Unit tests for approval workflow.

Tests the ApprovalRequest class and approval workflow functionality.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime
import sys

# Add My_AI_Employee to path (go up to My_AI_Employee root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from approval.approval_request import ApprovalRequest


@pytest.fixture
def mock_vault_path(tmp_path):
    """Create a temporary vault structure."""
    vault = tmp_path / "AI_Employee_Vault"
    pending = vault / "Pending_Approval"
    approved = vault / "Approved"
    rejected = vault / "Rejected"

    pending.mkdir(parents=True)
    approved.mkdir(parents=True)
    rejected.mkdir(parents=True)

    return str(vault)


@pytest.fixture
def approval_request(mock_vault_path):
    """Create an ApprovalRequest instance."""
    return ApprovalRequest(vault_path=mock_vault_path)


def test_approval_request_creation(approval_request, mock_vault_path):
    """Test creating an approval request."""
    action_item_path = Path(mock_vault_path) / "Needs_Action" / "test_item.md"
    action_item_path.parent.mkdir(parents=True, exist_ok=True)
    action_item_path.write_text("Test action item")

    plan_content = "Test plan content"
    draft_content = "Test draft content"

    result = approval_request.create(
        action_item_path=action_item_path,
        plan_content=plan_content,
        draft_content=draft_content,
        action_type='send_email'
    )

    assert result is not None
    assert result.exists()
    assert 'Pending_Approval' in str(result)


def test_approval_request_validation(approval_request):
    """Test approval request validation."""
    valid_content = """---
type: approval_request
action: send_email
status: pending
priority: medium
---
## Action Request
Test content
"""

    is_valid = approval_request.validate(valid_content)
    assert is_valid


def test_approval_request_invalid_format(approval_request):
    """Test approval request with invalid format."""
    invalid_content = "Invalid content without frontmatter"

    is_valid = approval_request.validate(invalid_content)
    assert not is_valid


def test_approval_request_move_to_approved(approval_request, mock_vault_path):
    """Test moving approval request to Approved/."""
    pending_path = Path(mock_vault_path) / "Pending_Approval"
    test_file = pending_path / "APPROVAL_test.md"
    test_file.write_text("Test approval content")

    result = approval_request.move_to_approved(test_file)

    assert result is not None
    assert 'Approved' in str(result)
    assert result.exists()
    assert not test_file.exists()


def test_approval_request_move_to_rejected(approval_request, mock_vault_path):
    """Test moving approval request to Rejected/."""
    pending_path = Path(mock_vault_path) / "Pending_Approval"
    test_file = pending_path / "APPROVAL_test.md"
    test_file.write_text("Test approval content")

    result = approval_request.move_to_rejected(test_file, reason="User rejected")

    assert result is not None
    assert 'Rejected' in str(result)
    assert result.exists()
    assert not test_file.exists()


def test_approval_request_count_pending(approval_request, mock_vault_path):
    """Test counting pending approval requests."""
    pending_path = Path(mock_vault_path) / "Pending_Approval"

    # Create test files
    for i in range(3):
        test_file = pending_path / f"APPROVAL_test_{i}.md"
        test_file.write_text("Test content")

    count = approval_request.count_pending()
    assert count == 3


def test_approval_request_expiration_check(approval_request):
    """Test checking if approval request is expired."""
    # Create expired approval
    expired_content = f"""---
type: approval_request
created: 2026-01-01T00:00:00Z
expires: 2026-01-02T00:00:00Z
---
Test content
"""

    is_expired = approval_request.is_expired(expired_content)
    assert is_expired


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
