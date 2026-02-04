"""
Integration tests for WhatsApp watcher.

Tests the WhatsAppWatcher class functionality with mocked Playwright.
Covers all 5 new features:
1. Preview-based reading (non-invasive)
2. Session expiration notification
3. CLI --init flag
4. Monitored contacts filter
5. Improved priority logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from datetime import datetime
import sys

# Add My_AI_Employee to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from watchers.whatsapp_watcher import WhatsAppWatcher


@pytest.fixture
def mock_vault_path(tmp_path):
    """Create a temporary vault structure."""
    vault = tmp_path / "AI_Employee_Vault"
    needs_action = vault / "Needs_Action"
    needs_action.mkdir(parents=True)

    # Create Company_Handbook.md with monitored contacts
    handbook = vault / "Company_Handbook.md"
    handbook.write_text("""# Company Handbook

## Monitored WhatsApp Contacts
- John Smith
- Sarah Johnson
- Tech Support Team
""")

    return str(vault)


@pytest.fixture
def whatsapp_watcher(mock_vault_path):
    """Create a WhatsAppWatcher instance with mocked dependencies."""
    with patch('watchers.whatsapp_watcher.sync_playwright'):
        watcher = WhatsAppWatcher(vault_path=mock_vault_path)
        return watcher


def test_whatsapp_watcher_initialization(mock_vault_path):
    """Test WhatsAppWatcher initializes correctly."""
    with patch('watchers.whatsapp_watcher.sync_playwright'):
        watcher = WhatsAppWatcher(vault_path=mock_vault_path)

        assert watcher.vault_path == Path(mock_vault_path)
        assert watcher.check_interval == 60
        assert isinstance(watcher.monitored_contacts, list)


def test_whatsapp_watcher_loads_monitored_contacts(mock_vault_path):
    """Test that monitored contacts are loaded from Company_Handbook.md."""
    with patch('watchers.whatsapp_watcher.sync_playwright'):
        watcher = WhatsAppWatcher(vault_path=mock_vault_path)

        assert len(watcher.monitored_contacts) == 3
        assert "John Smith" in watcher.monitored_contacts
        assert "Sarah Johnson" in watcher.monitored_contacts
        assert "Tech Support Team" in watcher.monitored_contacts


def test_whatsapp_watcher_urgent_keyword_detection(whatsapp_watcher):
    """Test that urgent keywords are detected correctly."""
    urgent_messages = [
        'URGENT: Need help with invoice',
        'This is an ASAP request',
        'HELP! System is down',
        'Payment issue - critical',
        'Emergency support needed'
    ]

    for message in urgent_messages:
        is_urgent = whatsapp_watcher._detect_urgent_keywords(message)
        assert is_urgent

    # Non-urgent message
    normal_message = 'Hello, how are you?'
    is_urgent = whatsapp_watcher._detect_urgent_keywords(normal_message)
    assert not is_urgent


def test_whatsapp_watcher_priority_logic_keywords(whatsapp_watcher):
    """Test improved priority logic based on keywords."""
    # High priority - urgent keyword
    high_priority_msg = {
        'body': 'URGENT: Need help immediately',
        'unread_count': 1
    }
    priority = whatsapp_watcher._determine_priority(high_priority_msg)
    assert priority == 'High'

    # High priority - payment keyword
    payment_msg = {
        'body': 'Payment issue with invoice',
        'unread_count': 1
    }
    priority = whatsapp_watcher._determine_priority(payment_msg)
    assert priority == 'High'


def test_whatsapp_watcher_priority_logic_unread_count(whatsapp_watcher):
    """Test improved priority logic based on unread count."""
    # High priority - 5+ unread messages
    high_unread_msg = {
        'body': 'Hello',
        'unread_count': 5
    }
    priority = whatsapp_watcher._determine_priority(high_unread_msg)
    assert priority == 'High'

    # Medium priority - 3-4 unread messages
    medium_unread_msg = {
        'body': 'Hello',
        'unread_count': 3
    }
    priority = whatsapp_watcher._determine_priority(medium_unread_msg)
    assert priority == 'Medium'

    # Medium priority - default
    normal_msg = {
        'body': 'Hello',
        'unread_count': 1
    }
    priority = whatsapp_watcher._determine_priority(normal_msg)
    assert priority == 'Medium'


def test_whatsapp_watcher_session_check_active(whatsapp_watcher):
    """Test that WhatsApp watcher checks session validity when active."""
    with patch.object(whatsapp_watcher, 'page') as mock_page:
        mock_page.wait_for_selector.return_value = True

        is_valid = whatsapp_watcher._check_session()
        assert is_valid
        assert whatsapp_watcher.session_active


def test_whatsapp_watcher_session_expired_creates_notification(whatsapp_watcher, mock_vault_path):
    """Test handling of expired WhatsApp session creates notification."""
    with patch.object(whatsapp_watcher, 'page') as mock_page:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

        # Mock QR code detection (session expired)
        mock_page.wait_for_selector.side_effect = [
            PlaywrightTimeoutError('Chat list timeout'),  # First call - no chat list
            True  # Second call - QR code found
        ]

        with patch.object(whatsapp_watcher, '_handle_session_expired') as mock_handle:
            is_valid = whatsapp_watcher._check_session()

            assert not is_valid
            assert not whatsapp_watcher.session_active
            mock_handle.assert_called_once()


def test_whatsapp_watcher_preview_based_reading(whatsapp_watcher):
    """Test that preview-based reading doesn't click into chats."""
    with patch.object(whatsapp_watcher, 'page') as mock_page:
        # Mock chat list with unread messages
        mock_chat = MagicMock()
        mock_unread_badge = MagicMock()
        mock_unread_badge.inner_text.return_value = '3'
        mock_contact_elem = MagicMock()
        mock_contact_elem.get_attribute.return_value = 'John Smith'
        mock_preview_elem = MagicMock()
        mock_preview_elem.inner_text.return_value = 'Hello, need help'
        mock_time_elem = MagicMock()
        mock_time_elem.inner_text.return_value = '10:30'

        mock_chat.query_selector.side_effect = [
            mock_unread_badge,  # unread badge
            mock_contact_elem,  # contact name
            mock_preview_elem,  # message preview
            mock_time_elem  # timestamp
        ]

        mock_page.wait_for_selector.return_value = True
        mock_page.query_selector_all.return_value = [mock_chat]

        messages = whatsapp_watcher._fetch_new_messages()

        # Verify no click() was called (non-invasive)
        mock_chat.click.assert_not_called()

        # Verify message was extracted from preview
        assert len(messages) == 1
        assert messages[0]['sender'] == 'John Smith'
        assert messages[0]['body'] == 'Hello, need help'
        assert messages[0]['unread_count'] == 3


def test_whatsapp_watcher_monitored_contacts_filter(whatsapp_watcher):
    """Test that only monitored contacts are processed."""
    with patch.object(whatsapp_watcher, 'page') as mock_page:
        # Mock two chats: one monitored, one not
        mock_chat_monitored = MagicMock()
        mock_chat_unmonitored = MagicMock()

        # Monitored contact (John Smith)
        mock_unread_badge_1 = MagicMock()
        mock_unread_badge_1.inner_text.return_value = '2'
        mock_contact_elem_1 = MagicMock()
        mock_contact_elem_1.get_attribute.return_value = 'John Smith'
        mock_preview_elem_1 = MagicMock()
        mock_preview_elem_1.inner_text.return_value = 'Test message'
        mock_time_elem_1 = MagicMock()
        mock_time_elem_1.inner_text.return_value = '10:30'

        mock_chat_monitored.query_selector.side_effect = [
            mock_unread_badge_1,
            mock_contact_elem_1,
            mock_preview_elem_1,
            mock_time_elem_1
        ]

        # Unmonitored contact (Random Person)
        mock_unread_badge_2 = MagicMock()
        mock_unread_badge_2.inner_text.return_value = '1'
        mock_contact_elem_2 = MagicMock()
        mock_contact_elem_2.get_attribute.return_value = 'Random Person'

        mock_chat_unmonitored.query_selector.side_effect = [
            mock_unread_badge_2,
            mock_contact_elem_2
        ]

        mock_page.wait_for_selector.return_value = True
        mock_page.query_selector_all.return_value = [mock_chat_monitored, mock_chat_unmonitored]

        messages = whatsapp_watcher._fetch_new_messages()

        # Only monitored contact should be included
        assert len(messages) == 1
        assert messages[0]['sender'] == 'John Smith'


def test_whatsapp_watcher_creates_action_item(whatsapp_watcher, mock_vault_path):
    """Test that WhatsApp watcher creates action items for urgent messages."""
    mock_message = {
        'sender': 'John Smith',
        'body': 'URGENT: Need invoice',
        'timestamp': '10:30',
        'date': datetime.now().isoformat(),
        'unread_count': 2
    }

    with patch('watchers.whatsapp_watcher.save_action_item') as mock_save:
        file_path = whatsapp_watcher.create_action_file(mock_message)

        # Verify action item was created
        mock_save.assert_called_once()
        assert file_path is not None
        assert 'whatsapp' in str(file_path)


def test_whatsapp_watcher_deduplication(whatsapp_watcher):
    """Test that duplicate messages are not processed twice."""
    message_id = 'test_message_123'

    # First processing
    whatsapp_watcher.dedupe_tracker.mark_processed(message_id)

    # Second processing - should be skipped
    assert whatsapp_watcher.dedupe_tracker.is_processed(message_id)


def test_whatsapp_watcher_initialize_session(whatsapp_watcher):
    """Test session initialization with QR code scan."""
    with patch.object(whatsapp_watcher, '_init_browser'):
        with patch.object(whatsapp_watcher, 'page') as mock_page:
            with patch.object(whatsapp_watcher, '_save_session'):
                with patch.object(whatsapp_watcher, '_close_browser'):
                    mock_page.wait_for_selector.return_value = True

                    success = whatsapp_watcher.initialize_session(timeout=10000)

                    assert success
                    mock_page.wait_for_selector.assert_called_with(
                        'div[data-testid="chat-list"]',
                        timeout=10000
                    )


def test_whatsapp_watcher_message_format_includes_notes(whatsapp_watcher, mock_vault_path):
    """Test that created action items include proper formatting notes."""
    mock_message = {
        'sender': 'John Smith',
        'body': 'Hello, how are you?',
        'timestamp': '10:30',
        'date': datetime.now().isoformat(),
        'unread_count': 1
    }

    with patch('watchers.whatsapp_watcher.save_action_item') as mock_save:
        whatsapp_watcher.create_action_file(mock_message)

        # Get the content passed to save_action_item
        call_args = mock_save.call_args[0][0]
        content = call_args.content

        # Verify formatting notes are included
        assert 'WhatsApp Format Note' in content
        assert 'Keep messages concise and conversational' in content
        assert 'Use line breaks for readability' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
