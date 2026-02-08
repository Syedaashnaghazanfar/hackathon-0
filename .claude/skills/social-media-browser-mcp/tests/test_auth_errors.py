"""
Unit tests for authentication error handling in Social Media Browser MCP.

Tests session expiration detection, error messages, re-login prompts for Facebook/Instagram/Twitter.
"""

import pytest
from enum import Enum
from typing import Optional, Dict
from dataclasses import dataclass
import tempfile
import shutil
from pathlib import Path


class AuthErrorType(Enum):
    """Types of authentication errors."""
    SESSION_EXPIRED = "session_expired"
    LOGIN_REQUIRED = "login_required"
    TOKEN_INVALID = "token_invalid"
    ACCOUNT_SUSPENDED = "account_suspended"
    RATE_LIMITED = "rate_limited"


@dataclass
class AuthError:
    """Authentication error details."""
    error_type: AuthErrorType
    platform: str
    message: str
    requires_relogin: bool
    suggested_action: str


class AuthErrorHandler:
    """Handle authentication errors for social media platforms."""

    # Platform-specific error indicators
    FACEBOOK_AUTH_ERRORS = [
        "session expired",
        "login required",
        "please log in",
        "authorization failed",
        "your session has expired"
    ]

    INSTAGRAM_AUTH_ERRORS = [
        "login required",
        "session expired",
        "please log in again",
        "you've been logged out"
    ]

    TWITTER_AUTH_ERRORS = [
        "authorization required",
        "session expired",
        "please sign in",
        "your session has expired",
        "authentication needed"
    ]

    @classmethod
    def detect_auth_error(cls, platform: str, page_text: str) -> Optional[AuthError]:
        """
        Detect if page shows authentication error.

        Args:
            platform: Platform name (facebook, instagram, twitter)
            page_text: Text content from page

        Returns:
            AuthError if detected, None otherwise
        """
        if not page_text:
            return None

        page_text_lower = page_text.lower()

        # Check platform-specific error messages
        if platform == "facebook":
            for error_indicator in cls.FACEBOOK_AUTH_ERRORS:
                if error_indicator in page_text_lower:
                    return AuthError(
                        error_type=AuthErrorType.SESSION_EXPIRED,
                        platform=platform,
                        message=f"Facebook session expired: {error_indicator}",
                        requires_relogin=True,
                        suggested_action="Run login_facebook.py to re-authenticate"
                    )

        elif platform == "instagram":
            for error_indicator in cls.INSTAGRAM_AUTH_ERRORS:
                if error_indicator in page_text_lower:
                    return AuthError(
                        error_type=AuthErrorType.SESSION_EXPIRED,
                        platform=platform,
                        message=f"Instagram session expired: {error_indicator}",
                        requires_relogin=True,
                        suggested_action="Run login_instagram.py to re-authenticate"
                    )

        elif platform == "twitter":
            for error_indicator in cls.TWITTER_AUTH_ERRORS:
                if error_indicator in page_text_lower:
                    return AuthError(
                        error_type=AuthErrorType.SESSION_EXPIRED,
                        platform=platform,
                        message=f"Twitter session expired: {error_indicator}",
                        requires_relogin=True,
                        suggested_action="Run login_twitter.py to re-authenticate"
                    )

        return None

    @classmethod
    def check_session_health(cls, platform: str, session_path: Path) -> Dict[str, any]:
        """
        Check health of saved session.

        Args:
            platform: Platform name
            session_path: Path to session directory

        Returns:
            Dict with health status
        """
        if not session_path.exists():
            return {
                "platform": platform,
                "healthy": False,
                "reason": "Session directory not found",
                "requires_relogin": True
            }

        # Check for required session files
        cookies_file = session_path / "cookies.json"
        storage_file = session_path / "storage_state.json"

        missing_files = []
        if not cookies_file.exists():
            missing_files.append("cookies.json")
        if not storage_file.exists():
            missing_files.append("storage_state.json")

        if missing_files:
            return {
                "platform": platform,
                "healthy": False,
                "reason": f"Missing session files: {', '.join(missing_files)}",
                "requires_relogin": True
            }

        # Check session age
        import time
        session_age_seconds = time.time() - session_path.stat().st_mtime
        session_age_hours = session_age_seconds / 3600

        # Sessions older than 24 hours may be stale
        if session_age_hours > 24:
            return {
                "platform": platform,
                "healthy": False,
                "reason": f"Session is {session_age_hours:.1f} hours old (may be expired)",
                "requires_relogin": True,
                "session_age_hours": session_age_hours
            }

        return {
            "platform": platform,
            "healthy": True,
            "session_age_hours": session_age_hours,
            "requires_relogin": False
        }

    @classmethod
    def format_relogin_prompt(cls, auth_error: AuthError) -> str:
        """
        Format user-friendly re-login prompt.

        Args:
            auth_error: Authentication error details

        Returns:
            Formatted prompt message
        """
        prompt = f"""
⚠️ Authentication Error Detected

Platform: {auth_error.platform.upper()}
Error: {auth_error.message}

Required Action: {auth_error.suggested_action}

Step-by-step:
1. Open terminal
2. Run: python {auth_error.suggested_action.split('Run ')[1]}
3. Complete login in browser window
4. Wait for session to be saved
5. Retry your action

After re-login, your session will be valid for ~24 hours.
"""
        return prompt.strip()


class TestAuthErrorDetection:
    """Test suite for authentication error detection."""

    def test_detect_facebook_session_expired(self):
        """Test detecting Facebook session expired error."""
        page_text = "Please log in to continue. Your session has expired."
        error = AuthErrorHandler.detect_auth_error("facebook", page_text)

        assert error is not None
        assert error.error_type == AuthErrorType.SESSION_EXPIRED
        assert error.platform == "facebook"
        assert error.requires_relogin is True
        assert "login_facebook.py" in error.suggested_action

    def test_detect_facebook_login_required(self):
        """Test detecting Facebook login required error."""
        page_text = "You must be logged in to view this page."
        error = AuthErrorHandler.detect_auth_error("facebook", page_text)

        assert error is not None
        assert error.platform == "facebook"

    def test_detect_instagram_session_expired(self):
        """Test detecting Instagram session expired error."""
        page_text = "Please log in again. You've been logged out."
        error = AuthErrorHandler.detect_auth_error("instagram", page_text)

        assert error is not None
        assert error.error_type == AuthErrorType.SESSION_EXPIRED
        assert error.platform == "instagram"
        assert "login_instagram.py" in error.suggested_action

    def test_detect_twitter_authorization_required(self):
        """Test detecting Twitter authorization required error."""
        page_text = "Authorization required. Please sign in."
        error = AuthErrorHandler.detect_auth_error("twitter", page_text)

        assert error is not None
        assert error.platform == "twitter"
        assert "login_twitter.py" in error.suggested_action

    def test_no_auth_error_in_normal_content(self):
        """Test normal content doesn't trigger auth error."""
        page_text = "Welcome to your news feed. Here are your latest posts."
        error = AuthErrorHandler.detect_auth_error("facebook", page_text)

        assert error is None

    def test_auth_error_case_insensitive(self):
        """Test auth error detection is case-insensitive."""
        page_text = "SESSION EXPIRED. PLEASE LOG IN."
        error = AuthErrorHandler.detect_auth_error("facebook", page_text)

        assert error is not None

    def test_auth_error_partial_match(self):
        """Test auth error detection with partial matches."""
        page_text = "Sorry, your session has expired. Please refresh."
        error = AuthErrorHandler.detect_auth_error("instagram", page_text)

        assert error is not None
        assert "session expired" in error.message.lower()


class TestSessionHealthCheck:
    """Test suite for session health checking."""

    @pytest.fixture
    def temp_session_dir(self):
        """Create temporary session directory for testing."""
        temp_dir = tempfile.mkdtemp()
        session_path = Path(temp_dir)
        yield session_path
        shutil.rmtree(temp_dir)

    def test_healthy_session_with_all_files(self, temp_session_dir):
        """Test healthy session with all required files."""
        # Create required files
        (temp_session_dir / "cookies.json").write_text("{}")
        (temp_session_dir / "storage_state.json").write_text("{}")

        health = AuthErrorHandler.check_session_health("facebook", temp_session_dir)

        assert health["healthy"] is True
        assert health["requires_relogin"] is False
        assert "session_age_hours" in health

    def test_missing_session_directory(self, temp_session_dir):
        """Test detection when session directory doesn't exist."""
        nonexistent_path = temp_session_dir / "nonexistent"

        health = AuthErrorHandler.check_session_health("instagram", nonexistent_path)

        assert health["healthy"] is False
        assert health["requires_relogin"] is True
        assert "not found" in health["reason"].lower()

    def test_missing_cookies_file(self, temp_session_dir):
        """Test detection when cookies.json is missing."""
        # Only create storage_state.json
        (temp_session_dir / "storage_state.json").write_text("{}")

        health = AuthErrorHandler.check_session_health("twitter", temp_session_dir)

        assert health["healthy"] is False
        assert health["requires_relogin"] is True
        assert "cookies.json" in health["reason"]

    def test_missing_storage_state_file(self, temp_session_dir):
        """Test detection when storage_state.json is missing."""
        # Only create cookies.json
        (temp_session_dir / "cookies.json").write_text("{}")

        health = AuthErrorHandler.check_session_health("facebook", temp_session_dir)

        assert health["healthy"] is False
        assert health["requires_relogin"] is True
        assert "storage_state.json" in health["reason"]

    def test_session_age_warning(self, temp_session_dir):
        """Test session age warning for old sessions."""
        # Create files
        (temp_session_dir / "cookies.json").write_text("{}")
        (temp_session_dir / "storage_state.json").write_text("{}")

        # Simulate old session by modifying mtime (25 hours ago)
        import time
        old_time = time.time() - (25 * 3600)
        (temp_session_dir / "cookies.json").touch(old_time)

        health = AuthErrorHandler.check_session_health("instagram", temp_session_dir)

        assert health["healthy"] is False
        assert health["requires_relogin"] is True
        assert health["session_age_hours"] > 24

    def test_fresh_session_considered_healthy(self, temp_session_dir):
        """Test fresh session (recent) is considered healthy."""
        # Create files
        (temp_session_dir / "cookies.json").write_text("{}")
        (temp_session_dir / "storage_state.json").write_text("{}")

        health = AuthErrorHandler.check_session_health("twitter", temp_session_dir)

        assert health["healthy"] is True
        assert health["session_age_hours"] < 1  # Very recent
        assert health["requires_relogin"] is False


class TestReloginPrompts:
    """Test suite for re-login prompt formatting."""

    def test_format_facebook_relogin_prompt(self):
        """Test formatting Facebook re-login prompt."""
        auth_error = AuthError(
            error_type=AuthErrorType.SESSION_EXPIRED,
            platform="facebook",
            message="Session expired",
            requires_relogin=True,
            suggested_action="Run login_facebook.py to re-authenticate"
        )

        prompt = AuthErrorHandler.format_relogin_prompt(auth_error)

        assert "⚠️" in prompt
        assert "Facebook" in prompt
        assert "login_facebook.py" in prompt
        assert "Step-by-step" in prompt

    def test_format_instagram_relogin_prompt(self):
        """Test formatting Instagram re-login prompt."""
        auth_error = AuthError(
            error_type=AuthErrorType.SESSION_EXPIRED,
            platform="instagram",
            message="Session expired",
            requires_relogin=True,
            suggested_action="Run login_instagram.py to re-authenticate"
        )

        prompt = AuthErrorHandler.format_relogin_prompt(auth_error)

        assert "Instagram" in prompt.upper()
        assert "login_instagram.py" in prompt

    def test_format_twitter_relogin_prompt(self):
        """Test formatting Twitter re-login prompt."""
        auth_error = AuthError(
            error_type=AuthErrorType.SESSION_EXPIRED,
            platform="twitter",
            message="Authorization required",
            requires_relogin=True,
            suggested_action="Run login_twitter.py to re-authenticate"
        )

        prompt = AuthErrorHandler.format_relogin_prompt(auth_error)

        assert "Twitter" in prompt.upper() or "twitter" in prompt
        assert "login_twitter.py" in prompt

    def test_prompt_includes_session_duration_info(self):
        """Test prompt mentions session duration."""
        auth_error = AuthError(
            error_type=AuthErrorType.SESSION_EXPIRED,
            platform="facebook",
            message="Session expired",
            requires_relogin=True,
            suggested_action="Run login_facebook.py to re-authenticate"
        )

        prompt = AuthErrorHandler.format_relogin_prompt(auth_error)

        assert "24 hours" in prompt

    def test_prompt_structure_has_all_sections(self):
        """Test prompt has all required sections."""
        auth_error = AuthError(
            error_type=AuthErrorType.SESSION_EXPIRED,
            platform="instagram",
            message="Session expired",
            requires_relogin=True,
            suggested_action="Run login_instagram.py to re-authenticate"
        )

        prompt = AuthErrorHandler.format_relogin_prompt(auth_error)

        # Check sections
        assert "Authentication Error Detected" in prompt
        assert "Platform:" in prompt
        assert "Error:" in prompt
        assert "Required Action:" in prompt
        assert "Step-by-step:" in prompt


class TestMultiPlatformAuthErrors:
    """Test suite for handling auth errors across multiple platforms."""

    def test_different_platforms_different_errors(self):
        """Test each platform has unique error messages."""
        facebook_page = "Facebook session expired"
        instagram_page = "Instagram login required"
        twitter_page = "Twitter authorization required"

        fb_error = AuthErrorHandler.detect_auth_error("facebook", facebook_page)
        ig_error = AuthErrorHandler.detect_auth_error("instagram", instagram_page)
        tw_error = AuthErrorHandler.detect_auth_error("twitter", twitter_page)

        assert fb_error.platform == "facebook"
        assert ig_error.platform == "instagram"
        assert tw_error.platform == "twitter"

    def test_check_multiple_platforms_health(self):
        """Test checking health for multiple platforms."""
        temp_dirs = []

        try:
            # Create temp directories
            for platform in ["facebook", "instagram", "twitter"]:
                temp_dir = tempfile.mkdtemp()
                temp_dirs.append(temp_dir)

                # Create healthy session
                Path(temp_dir, "cookies.json").write_text("{}")
                Path(temp_dir, "storage_state.json").write_text("{}")

            # Check all platforms
            results = []
            platforms = ["facebook", "instagram", "twitter"]
            for i, platform in enumerate(platforms):
                health = AuthErrorHandler.check_session_health(platform, Path(temp_dirs[i]))
                results.append(health)

            # All should be healthy
            assert all(r["healthy"] for r in results)
            assert all(r["platform"] == platforms[i] for i, r in enumerate(results))

        finally:
            # Cleanup
            for temp_dir in temp_dirs:
                shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
