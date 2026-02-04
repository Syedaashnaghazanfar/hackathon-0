"""
Unit tests for orchestrator.

Tests the Orchestrator class functionality with mocked MCP servers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add My_AI_Employee to path (go up to My_AI_Employee root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator import Orchestrator


@pytest.fixture
def mock_vault_path(tmp_path):
    """Create a temporary vault structure."""
    vault = tmp_path / "AI_Employee_Vault"
    approved = vault / "Approved"
    done = vault / "Done"
    failed = vault / "Failed"
    logs = vault / "Logs"

    approved.mkdir(parents=True)
    done.mkdir(parents=True)
    failed.mkdir(parents=True)
    logs.mkdir(parents=True)

    return str(vault)


@pytest.fixture
def orchestrator(mock_vault_path):
    """Create an Orchestrator instance."""
    return Orchestrator(vault_path=mock_vault_path)


def test_orchestrator_initialization(mock_vault_path):
    """Test Orchestrator initializes correctly."""
    orch = Orchestrator(vault_path=mock_vault_path)

    assert orch.vault_path == Path(mock_vault_path)
    assert orch.approved_path.exists()
    assert orch.done_path.exists()
    assert orch.failed_path.exists()


def test_orchestrator_routes_email_action(orchestrator):
    """Test that email actions are routed to email_mcp."""
    approval_content = """---
type: approval_request
action: send_email
mcp_server: email-mcp
---
## Parameters
- To: test@example.com
- Subject: Test
- Body: Test body
"""

    with patch.object(orchestrator, '_execute_email_action') as mock_execute:
        mock_execute.return_value = {'status': 'success', 'message_id': '123'}

        result = orchestrator._route_action('send_email', approval_content, 'test_entry')

        assert mock_execute.called
        assert result['status'] == 'success'


def test_orchestrator_routes_linkedin_action(orchestrator):
    """Test that LinkedIn actions are routed to linkedin_mcp."""
    approval_content = """---
type: approval_request
action: linkedin_post
mcp_server: linkedin-mcp
---
## Parameters
- Content: Test post
"""

    with patch.object(orchestrator, '_execute_linkedin_action') as mock_execute:
        mock_execute.return_value = {'status': 'success', 'post_id': '123'}

        result = orchestrator._route_action('linkedin_post', approval_content, 'test_entry')

        assert mock_execute.called
        assert result['status'] == 'success'


def test_orchestrator_retry_logic(orchestrator):
    """Test that orchestrator retries failed actions."""
    with patch.object(orchestrator, '_execute_email_action') as mock_execute:
        # Fail twice, succeed on third attempt
        mock_execute.side_effect = [
            {'status': 'error', 'error': 'Temporary failure'},
            {'status': 'error', 'error': 'Temporary failure'},
            {'status': 'success', 'message_id': '123'}
        ]

        result = orchestrator._execute_with_retry('send_email', {}, 'test_entry')

        assert mock_execute.call_count == 3
        assert result['status'] == 'success'


def test_orchestrator_max_retries_exceeded(orchestrator):
    """Test that orchestrator stops after max retries."""
    with patch.object(orchestrator, '_execute_email_action') as mock_execute:
        # Always fail
        mock_execute.return_value = {'status': 'error', 'error': 'Permanent failure'}

        result = orchestrator._execute_with_retry('send_email', {}, 'test_entry')

        assert mock_execute.call_count == 3  # Max retries
        assert result['status'] == 'error'


def test_orchestrator_moves_success_to_done(orchestrator, mock_vault_path):
    """Test that successful actions are moved to Done/."""
    approved_path = Path(mock_vault_path) / "Approved"
    test_file = approved_path / "APPROVAL_test.md"
    test_file.write_text("Test approval content")

    with patch.object(orchestrator, '_route_action') as mock_route:
        mock_route.return_value = {'status': 'success', 'message_id': '123'}

        orchestrator._process_approval_file(test_file)

        # File should be moved to Done/
        done_file = Path(mock_vault_path) / "Done" / "APPROVAL_test.md"
        assert done_file.exists()
        assert not test_file.exists()


def test_orchestrator_moves_failure_to_failed(orchestrator, mock_vault_path):
    """Test that failed actions are moved to Failed/."""
    approved_path = Path(mock_vault_path) / "Approved"
    test_file = approved_path / "APPROVAL_test.md"
    test_file.write_text("Test approval content")

    with patch.object(orchestrator, '_route_action') as mock_route:
        mock_route.return_value = {'status': 'error', 'error': 'Execution failed'}

        orchestrator._process_approval_file(test_file)

        # File should be moved to Failed/
        failed_file = Path(mock_vault_path) / "Failed" / "APPROVAL_test.md"
        assert failed_file.exists()
        assert not test_file.exists()


def test_orchestrator_audit_logging(orchestrator):
    """Test that all actions are logged to audit log."""
    with patch.object(orchestrator, '_route_action') as mock_route:
        with patch.object(orchestrator, 'audit_logger') as mock_logger:
            mock_route.return_value = {'status': 'success', 'message_id': '123'}

            orchestrator._execute_action('send_email', {}, 'test_entry')

            # Verify audit logging was called
            assert mock_logger.log_execution.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
