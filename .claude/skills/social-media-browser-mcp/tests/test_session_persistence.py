"""
Unit tests for session persistence in Social Media Browser MCP.

Tests browser context saves/loads from .social_session/, verifies cookies
persist across restarts for Facebook, Instagram, and Twitter/X.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta


# Mock implementation (will be replaced by actual implementation)
class SocialMediaBrowser:
    """Manage Playwright browser contexts for social media platforms."""

    def __init__(self, session_dir: str = ".social_session"):
        """
        Initialize browser session manager.

        Args:
            session_dir: Directory to store session data
        """
        self.session_dir = Path(session_dir)
        self.contexts = {}

    def save_context(self, platform: str, context_id: str, cookies: list,
                     storage_state: dict) -> None:
        """
        Save browser context to disk.

        Args:
            platform: Platform name (facebook, instagram, twitter)
            context_id: Unique context identifier
            cookies: List of cookie dictionaries
            storage_state: Browser storage state (localStorage, sessionStorage)
        """
        platform_dir = self.session_dir / platform
        platform_dir.mkdir(parents=True, exist_ok=True)

        # Save cookies
        cookies_file = platform_dir / f"{context_id}_cookies.json"
        import json
        with open(cookies_file, 'w') as f:
            json.dump(cookies, f)

        # Save storage state
        storage_file = platform_dir / f"{context_id}_storage.json"
        with open(storage_file, 'w') as f:
            json.dump(storage_state, f)

    def load_context(self, platform: str, context_id: str) -> tuple[list, dict]:
        """
        Load browser context from disk.

        Args:
            platform: Platform name (facebook, instagram, twitter)
            context_id: Unique context identifier

        Returns:
            Tuple of (cookies list, storage state dict)

        Raises:
            FileNotFoundError: If session files don't exist
        """
        platform_dir = self.session_dir / platform
        cookies_file = platform_dir / f"{context_id}_cookies.json"
        storage_file = platform_dir / f"{context_id}_storage.json"

        import json
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)

        with open(storage_file, 'r') as f:
            storage_state = json.load(f)

        return cookies, storage_state

    def context_exists(self, platform: str, context_id: str) -> bool:
        """
        Check if context files exist.

        Args:
            platform: Platform name
            context_id: Context identifier

        Returns:
            True if both cookies and storage files exist
        """
        platform_dir = self.session_dir / platform
        cookies_file = platform_dir / f"{context_id}_cookies.json"
        storage_file = platform_dir / f"{context_id}_storage.json"
        return cookies_file.exists() and storage_file.exists()

    def get_session_age(self, platform: str, context_id: str) -> Optional[float]:
        """
        Get session age in hours.

        Args:
            platform: Platform name
            context_id: Context identifier

        Returns:
            Age in hours, or None if session doesn't exist
        """
        platform_dir = self.session_dir / platform
        cookies_file = platform_dir / f"{context_id}_cookies.json"

        if not cookies_file.exists():
            return None

        mtime = cookies_file.stat().st_mtime
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        return age_hours


class TestSessionPersistence:
    """Test suite for browser session persistence."""

    @pytest.fixture
    def temp_session_dir(self):
        """Create temporary directory for session tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_save_facebook_context(self, temp_session_dir):
        """Test saving Facebook browser context to disk."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        cookies = [
            {"name": "datr", "value": "test_value", "domain": ".facebook.com"},
            {"name": "sb", "value": "test_sb", "domain": ".facebook.com"}
        ]
        storage_state = {
            "localStorage": {"key": "value"},
            "sessionStorage": {"session_key": "session_value"}
        }

        browser.save_context("facebook", "ctx_001", cookies, storage_state)

        # Verify files were created
        session_path = Path(temp_session_dir) / "facebook"
        assert (session_path / "ctx_001_cookies.json").exists()
        assert (session_path / "ctx_001_storage.json").exists()

    def test_load_facebook_context(self, temp_session_dir):
        """Test loading Facebook browser context from disk."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        # First save a context
        original_cookies = [
            {"name": "datr", "value": "test_value", "domain": ".facebook.com"}
        ]
        original_storage = {
            "localStorage": {"key": "value"}
        }
        browser.save_context("facebook", "ctx_002", original_cookies, original_storage)

        # Load the context
        loaded_cookies, loaded_storage = browser.load_context("facebook", "ctx_002")

        # Verify data matches
        assert loaded_cookies == original_cookies
        assert loaded_storage == original_storage

    def test_context_exists_true(self, temp_session_dir):
        """Test context_exists returns True when files exist."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        browser.save_context("instagram", "ctx_003", [], {})

        assert browser.context_exists("instagram", "ctx_003") is True

    def test_context_exists_false(self, temp_session_dir):
        """Test context_exists returns False when files don't exist."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        assert browser.context_exists("twitter", "nonexistent") is False

    def test_get_session_age_recent(self, temp_session_dir):
        """Test get_session_age returns age for recent session."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        browser.save_context("facebook", "ctx_004", [], {})

        age = browser.get_session_age("facebook", "ctx_004")
        assert age is not None
        assert age < 1.0  # Less than 1 hour old

    def test_get_session_age_none(self, temp_session_dir):
        """Test get_session_age returns None for nonexistent session."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        age = browser.get_session_age("facebook", "nonexistent")
        assert age is None

    def test_multiple_platforms_isolated(self, temp_session_dir):
        """Test sessions for different platforms are isolated."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        # Save contexts for different platforms
        browser.save_context("facebook", "ctx_005", [{"name": "fb_cookie"}], {})
        browser.save_context("instagram", "ctx_006", [{"name": "ig_cookie"}], {})
        browser.save_context("twitter", "ctx_007", [{"name": "tw_cookie"}], {})

        # Verify each platform has its own directory
        session_path = Path(temp_session_dir)
        assert (session_path / "facebook" / "ctx_005_cookies.json").exists()
        assert (session_path / "instagram" / "ctx_006_cookies.json").exists()
        assert (session_path / "twitter" / "ctx_007_cookies.json").exists()

    def test_multiple_contexts_same_platform(self, temp_session_dir):
        """Test multiple contexts can be saved for same platform."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        browser.save_context("facebook", "ctx_008", [{"name": "cookie1"}], {})
        browser.save_context("facebook", "ctx_009", [{"name": "cookie2"}], {})

        # Verify both contexts exist
        assert browser.context_exists("facebook", "ctx_008") is True
        assert browser.context_exists("facebook", "ctx_009") is True

    def test_load_nonexistent_context_raises_error(self, temp_session_dir):
        """Test loading nonexistent context raises FileNotFoundError."""
        browser = SocialMediaBrowser(session_dir=temp_session_dir)

        with pytest.raises(FileNotFoundError):
            browser.load_context("facebook", "nonexistent_ctx")

    def test_session_persistence_across_restarts(self, temp_session_dir):
        """Test cookies persist across browser restarts (simulated)."""
        # First "browser instance" saves context
        browser1 = SocialMediaBrowser(session_dir=temp_session_dir)
        original_cookies = [
            {"name": "session_key", "value": "abc123", "domain": ".facebook.com"}
        ]
        browser1.save_context("facebook", "ctx_010", original_cookies, {})

        # Simulate browser restart by creating new instance
        browser2 = SocialMediaBrowser(session_dir=temp_session_dir)
        loaded_cookies, _ = browser2.load_context("facebook", "ctx_010")

        # Verify cookies persisted
        assert loaded_cookies == original_cookies

    def test_session_age_increases_over_time(self, temp_session_dir):
        """Test session age calculation increases over time."""
        import time

        browser = SocialMediaBrowser(session_dir=temp_session_dir)
        browser.save_context("facebook", "ctx_011", [], {})

        # Get initial age
        age1 = browser.get_session_age("facebook", "ctx_011")

        # Wait a bit and check age increased
        time.sleep(0.1)  # 100ms
        age2 = browser.get_session_age("facebook", "ctx_011")

        assert age2 > age1
        assert (age2 - age1) < 0.01  # Should be ~0.0028 hours (100ms)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
