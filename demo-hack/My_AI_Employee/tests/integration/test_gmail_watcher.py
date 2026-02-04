"""
Unit tests for Gmail watcher.

Tests the GmailWatcher class functionality with mocked Gmail API.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import sys

# Add My_AI_Employee to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from watchers.gmail_watcher import GmailWatcher


@pytest.fixture
def mock_vault_path(tmp_path):
    """Create a temporary vault structure."""
    vault = tmp_path / "AI_Employee_Vault"
    needs_action = vault / "Needs_Action"
    needs_action.mkdir(parents=True)
    return str(vault)


@pytest.fixture
def mock_gmail_service():
    """Create a mock Gmail service."""
    service = MagicMock()
    return service


@pytest.fixture
def gmail_watcher(mock_vault_path):
    """Create a GmailWatcher instance with mocked dependencies."""
    with patch('watchers.gmail_watcher.OAuth2Helper'):
        watcher = GmailWatcher(vault_path=mock_vault_path)
        return watcher


def test_gmail_watcher_initialization(mock_vault_path):
    """Test GmailWatcher initializes correctly."""
    with patch('watchers.gmail_watcher.OAuth2Helper'):
        watcher = GmailWatcher(vault_path=mock_vault_path)

        assert watcher.vault_path == Path(mock_vault_path)
        assert watcher.needs_action_path.exists()
        assert watcher.check_interval == 60  # Default from .env


def test_gmail_watcher_creates_action_item(gmail_watcher, mock_vault_path):
    """Test that Gmail watcher creates action items from emails."""
    # Mock email data
    mock_message = {
        'id': 'test_message_123',
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'client@example.com'},
                {'name': 'Subject', 'value': 'Urgent: Project Update'},
                {'name': 'Date', 'value': 'Mon, 17 Jan 2026 10:00:00 +0000'}
            ],
            'body': {
                'data': 'VGVzdCBlbWFpbCBib2R5'  # Base64 encoded "Test email body"
            }
        }
    }

    with patch.object(gmail_watcher, '_fetch_new_messages', return_value=[mock_message]):
        with patch.object(gmail_watcher, '_create_action_item') as mock_create:
            gmail_watcher._process_messages()

            # Verify action item creation was called
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert call_args['sender'] == 'client@example.com'
            assert 'Urgent' in call_args['subject']


def test_gmail_watcher_deduplication(gmail_watcher):
    """Test that duplicate emails are not processed twice."""
    message_id = 'test_message_123'

    # First processing
    gmail_watcher.dedupe_tracker.mark_processed(message_id)

    # Second processing - should be skipped
    assert gmail_watcher.dedupe_tracker.is_processed(message_id)


def test_gmail_watcher_priority_detection(gmail_watcher):
    """Test that priority is correctly detected from email content."""
    # High priority keywords
    high_priority_subjects = [
        'URGENT: Need help',
        'ASAP: Project deadline',
        'CRITICAL: System down'
    ]

    for subject in high_priority_subjects:
        priority = gmail_watcher._detect_priority(subject, '')
        assert priority == 'high'

    # Medium priority
    medium_subject = 'Question about invoice'
    priority = gmail_watcher._detect_priority(medium_subject, '')
    assert priority == 'medium'


def test_gmail_watcher_error_handling(gmail_watcher):
    """Test that Gmail watcher handles API errors gracefully."""
    with patch.object(gmail_watcher, '_fetch_new_messages', side_effect=Exception('API Error')):
        # Should not raise exception
        try:
            gmail_watcher._process_messages()
        except Exception:
            pytest.fail("Gmail watcher should handle errors gracefully")


def test_gmail_watcher_oauth_token_refresh(gmail_watcher):
    """Test that OAuth token is refreshed when expired."""
    with patch.object(gmail_watcher.auth_helper, 'get_credentials') as mock_creds:
        mock_creds.return_value = Mock(expired=True)

        # Should trigger token refresh
        gmail_watcher._ensure_authenticated()

        # Verify refresh was attempted
        assert mock_creds.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
