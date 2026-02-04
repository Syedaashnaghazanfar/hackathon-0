"""
Unit tests for browser MCP server.

Tests the browser_mcp server functionality with mocked Playwright.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add My_AI_Employee to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_servers.browser_mcp import send_whatsapp_message, health_check


@pytest.fixture
def mock_browser():
    """Create a mock Playwright browser."""
    browser = MagicMock()
    page = MagicMock()
    browser.new_page.return_value = page
    return browser, page


def test_send_whatsapp_message_success(mock_browser):
    """Test successful WhatsApp message sending."""
    browser, page = mock_browser

    with patch('mcp_servers.browser_mcp.sync_playwright') as mock_playwright:
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = browser

        result = send_whatsapp_message(
            contact='Test Contact',
            message='Test message',
            entry_id='test_entry_123'
        )

        assert result['status'] == 'sent'
        assert 'message_id' in result


def test_send_whatsapp_message_contact_not_found(mock_browser):
    """Test WhatsApp message sending when contact not found."""
    browser, page = mock_browser
    page.click.side_effect = Exception('Contact not found')

    with patch('mcp_servers.browser_mcp.sync_playwright') as mock_playwright:
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = browser

        result = send_whatsapp_message(
            contact='Nonexistent Contact',
            message='Test message'
        )

        assert result['status'] == 'error'
        assert 'error' in result


def test_send_whatsapp_message_dry_run_mode():
    """Test WhatsApp message sending in DRY_RUN mode."""
    with patch('mcp_servers.browser_mcp.os.getenv', return_value='true'):
        result = send_whatsapp_message(
            contact='Test Contact',
            message='Test message'
        )

        assert result['status'] == 'dry_run'
        assert 'message' in result


def test_health_check_success(mock_browser):
    """Test health check with valid WhatsApp session."""
    browser, page = mock_browser
    page.wait_for_selector.return_value = True

    with patch('mcp_servers.browser_mcp.sync_playwright') as mock_playwright:
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = browser

        result = health_check()

        assert result['status'] == 'available'
        assert result['service'] == 'whatsapp'


def test_health_check_session_expired(mock_browser):
    """Test health check when WhatsApp session is expired."""
    browser, page = mock_browser
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    page.wait_for_selector.side_effect = PlaywrightTimeoutError('Timeout')

    with patch('mcp_servers.browser_mcp.sync_playwright') as mock_playwright:
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = browser

        result = health_check()

        assert result['status'] == 'unavailable'
        assert 'error' in result


def test_send_whatsapp_message_audit_logging():
    """Test that WhatsApp messages are logged to audit log."""
    with patch('mcp_servers.browser_mcp.sync_playwright'):
        with patch('mcp_servers.browser_mcp.AuditLogger') as mock_logger:
            send_whatsapp_message(
                contact='Test Contact',
                message='Test message',
                entry_id='test_123'
            )

            # Verify audit logging was called
            assert mock_logger.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
