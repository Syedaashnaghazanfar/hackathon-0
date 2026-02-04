"""
Unit tests for Email MCP server.

Tests the email_mcp server functionality with mocked Gmail API.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add My_AI_Employee to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_servers.email_mcp import send_email, health_check


@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service."""
    service = MagicMock()
    service.users().messages().send().execute.return_value = {
        'id': 'test_message_123',
        'labelIds': ['SENT']
    }
    return service


def test_send_email_success(mock_gmail_service):
    """Test successful email sending."""
    with patch('mcp_servers.email_mcp.build_gmail_service', return_value=mock_gmail_service):
        result = send_email(
            to='recipient@example.com',
            subject='Test Subject',
            body='Test body content',
            entry_id='test_entry_123'
        )

        assert result['status'] == 'sent'
        assert 'message_id' in result
        assert result['message_id'] == 'test_message_123'


def test_send_email_with_html(mock_gmail_service):
    """Test sending HTML email."""
    with patch('mcp_servers.email_mcp.build_gmail_service', return_value=mock_gmail_service):
        result = send_email(
            to='recipient@example.com',
            subject='Test Subject',
            body='<h1>Test HTML</h1>',
            is_html=True
        )

        assert result['status'] == 'sent'


def test_send_email_invalid_recipient():
    """Test email sending with invalid recipient."""
    with patch('mcp_servers.email_mcp.build_gmail_service') as mock_build:
        mock_service = MagicMock()
        mock_service.users().messages().send().execute.side_effect = Exception('Invalid recipient')
        mock_build.return_value = mock_service

        result = send_email(
            to='invalid-email',
            subject='Test',
            body='Test'
        )

        assert result['status'] == 'error'
        assert 'error' in result


def test_send_email_dry_run_mode():
    """Test email sending in DRY_RUN mode."""
    with patch('mcp_servers.email_mcp.os.getenv', return_value='true'):
        result = send_email(
            to='recipient@example.com',
            subject='Test',
            body='Test'
        )

        assert result['status'] == 'dry_run'
        assert 'message' in result


def test_health_check_success():
    """Test health check with working Gmail API."""
    with patch('mcp_servers.email_mcp.build_gmail_service') as mock_build:
        mock_service = MagicMock()
        mock_service.users().getProfile().execute.return_value = {
            'emailAddress': 'test@example.com'
        }
        mock_build.return_value = mock_service

        result = health_check()

        assert result['status'] == 'available'
        assert result['service'] == 'gmail'


def test_health_check_failure():
    """Test health check when Gmail API is unavailable."""
    with patch('mcp_servers.email_mcp.build_gmail_service', side_effect=Exception('API Error')):
        result = health_check()

        assert result['status'] == 'unavailable'
        assert 'error' in result


def test_send_email_audit_logging():
    """Test that email sending is logged to audit log."""
    with patch('mcp_servers.email_mcp.build_gmail_service') as mock_build:
        with patch('mcp_servers.email_mcp.AuditLogger') as mock_logger:
            mock_service = MagicMock()
            mock_service.users().messages().send().execute.return_value = {'id': '123'}
            mock_build.return_value = mock_service

            send_email(
                to='recipient@example.com',
                subject='Test',
                body='Test',
                entry_id='test_123'
            )

            # Verify audit logging was called
            assert mock_logger.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
