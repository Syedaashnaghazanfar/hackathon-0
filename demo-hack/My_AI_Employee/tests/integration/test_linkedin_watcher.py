"""
Unit tests for LinkedIn watcher.

Tests the LinkedInWatcher class functionality with mocked Playwright.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import sys

# Add My_AI_Employee to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from watchers.linkedin_watcher import LinkedInWatcher


@pytest.fixture
def mock_vault_path(tmp_path):
    """Create a temporary vault structure."""
    vault = tmp_path / "AI_Employee_Vault"
    needs_action = vault / "Needs_Action"
    needs_action.mkdir(parents=True)
    return str(vault)


@pytest.fixture
def linkedin_watcher(mock_vault_path):
    """Create a LinkedInWatcher instance with mocked dependencies."""
    with patch('watchers.linkedin_watcher.sync_playwright'):
        watcher = LinkedInWatcher(vault_path=mock_vault_path)
        return watcher


def test_linkedin_watcher_initialization(mock_vault_path):
    """Test LinkedInWatcher initializes correctly."""
    with patch('watchers.linkedin_watcher.sync_playwright'):
        watcher = LinkedInWatcher(vault_path=mock_vault_path)

        assert watcher.vault_path == Path(mock_vault_path)
        assert watcher.check_interval == 300  # 5 minutes


def test_linkedin_watcher_schedule_detection(linkedin_watcher):
    """Test that LinkedIn watcher detects correct posting schedule."""
    # Mock Monday at 9:00 AM
    with patch('watchers.linkedin_watcher.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 1, 19, 9, 0)  # Monday
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        should_post = linkedin_watcher._check_schedule()
        assert should_post

    # Mock Tuesday at 9:00 AM (should not post)
    with patch('watchers.linkedin_watcher.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2026, 1, 20, 9, 0)  # Tuesday
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        should_post = linkedin_watcher._check_schedule()
        assert not should_post


def test_linkedin_watcher_content_generation(linkedin_watcher):
    """Test that LinkedIn watcher generates post content."""
    content = linkedin_watcher._generate_post_content()

    assert content is not None
    assert len(content) > 0
    assert len(content) <= 280  # LinkedIn character limit


def test_linkedin_watcher_deduplication(linkedin_watcher):
    """Test that duplicate posts are not created."""
    post_id = 'test_post_123'

    # First post
    linkedin_watcher.dedupe_tracker.mark_processed(post_id)

    # Second post - should be skipped
    assert linkedin_watcher.dedupe_tracker.is_processed(post_id)


def test_linkedin_watcher_rate_limiting(linkedin_watcher):
    """Test that LinkedIn watcher respects rate limits."""
    # Mock rate limit file
    with patch.object(linkedin_watcher, '_check_rate_limit') as mock_check:
        mock_check.return_value = False  # Rate limit exceeded

        can_post = linkedin_watcher._can_post_now()
        assert not can_post


def test_linkedin_watcher_creates_action_item(linkedin_watcher, mock_vault_path):
    """Test that LinkedIn watcher creates action items for posts."""
    with patch.object(linkedin_watcher, '_check_schedule', return_value=True):
        with patch.object(linkedin_watcher, '_can_post_now', return_value=True):
            with patch.object(linkedin_watcher, '_create_post_action_item') as mock_create:
                linkedin_watcher._process_scheduled_post()

                # Verify action item creation was called
                mock_create.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
