"""
Centralized configuration for Silver Tier AI Employee.

Loads all settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars only


@dataclass
class Config:
    """
    Centralized configuration dataclass.

    All settings loaded from .env file or environment variables.
    """

    # Vault Configuration
    vault_root: Path

    # Gmail MCP Server
    gmail_credentials_file: str
    gmail_token_file: str
    gmail_scopes: str

    # LinkedIn MCP Server
    linkedin_access_token: str
    linkedin_person_urn: str

    # WhatsApp Browser Automation
    whatsapp_session_dir: str  # Directory containing session.json file
    whatsapp_cdp_port: int  # Not used in new implementation (kept for compatibility)
    whatsapp_headless: bool  # Run browser in headless mode

    # Global Settings
    dry_run: bool
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    check_interval: int  # Watcher polling interval (seconds)

    # MCP Executor
    orchestrator_check_interval: int  # How often to check /Approved/ folder

    # =============================================================================
    # GOLD TIER: Social Media Monitoring (User Story 4)
    # =============================================================================
    # Enable/disable social media monitoring
    social_watcher_enabled: bool

    # Social media watcher polling interval (seconds)
    social_watcher_interval: int

    # Priority keywords (comma-separated, case-insensitive)
    # HIGH priority: urgent customer inquiries
    social_high_priority_keywords: str

    # MEDIUM priority: business opportunities
    social_business_keywords: str

    # Whitelist accounts (comma-separated)
    # If set, ONLY process interactions from these accounts
    social_whitelist_accounts: str

    # Engagement thresholds (viral detection)
    social_fb_reaction_threshold: int
    social_ig_comment_threshold: int
    social_twitter_mention_threshold: int

    # Daily summary generation time (24-hour format, user's timezone)
    social_summary_time: str

    # Platform-specific enable/disable
    social_facebook_enabled: bool
    social_instagram_enabled: bool
    social_twitter_enabled: bool

    # =============================================================================
    # GOLD TIER: Social Media Posting (User Story 2 - Partial)
    # =============================================================================
    # Directory for social media browser sessions (gitignored)
    social_session_dir: str

    # Chrome DevTools Protocol ports for each platform (must be unique)
    social_fb_cdp_port: int
    social_ig_cdp_port: int
    social_tw_cdp_port: int

    @classmethod
    def load_from_env(cls) -> "Config":
        """
        Load configuration from environment variables.

        Returns:
            Config instance with all settings

        Raises:
            ValueError: If required environment variables are missing

        Example:
            >>> config = Config.load_from_env()
            >>> config.dry_run
            True
            >>> config.vault_root
            Path('AI_Employee_Vault')
        """
        # Vault Configuration
        vault_root = Path(os.getenv("VAULT_ROOT", "AI_Employee_Vault"))

        # Gmail MCP Server
        gmail_credentials_file = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
        gmail_token_file = os.getenv("GMAIL_TOKEN_FILE", "token.json")
        gmail_scopes = os.getenv("GMAIL_SCOPES", "https://www.googleapis.com/auth/gmail.modify")

        # LinkedIn MCP Server
        linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        linkedin_person_urn = os.getenv("LINKEDIN_PERSON_URN", "")

        # WhatsApp Browser Automation
        whatsapp_session_dir = os.getenv("WHATSAPP_SESSION_DIR", ".whatsapp_session")
        whatsapp_cdp_port = int(os.getenv("WHATSAPP_CDP_PORT", "9222"))
        whatsapp_headless = os.getenv("WHATSAPP_HEADLESS", "true").lower() in ("true", "1", "yes")

        # Global Settings
        dry_run = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        check_interval = int(os.getenv("CHECK_INTERVAL", "60"))

        # MCP Executor
        orchestrator_check_interval = int(os.getenv("ORCHESTRATOR_CHECK_INTERVAL", "10"))

        # =============================================================================
        # GOLD TIER: Social Media Monitoring
        # =============================================================================
        # Enable/disable social media monitoring
        social_watcher_enabled = os.getenv("SOCIAL_WATCHER_ENABLED", "false").lower() in ("true", "1", "yes")

        # Social media watcher polling interval (default: 600 = 10 minutes)
        social_watcher_interval = int(os.getenv("SOCIAL_WATCHER_INTERVAL", "600"))

        # Priority keywords (comma-separated)
        social_high_priority_keywords = os.getenv(
            "SOCIAL_HIGH_PRIORITY_KEYWORDS",
            "urgent,help,pricing,cost,invoice,payment,client,emergency"
        )

        social_business_keywords = os.getenv(
            "SOCIAL_BUSINESS_KEYWORDS",
            "project,services,quote,proposal,consulting,hire,contract"
        )

        # Whitelist accounts (comma-separated, empty = all accounts)
        social_whitelist_accounts = os.getenv("SOCIAL_WHITELIST_ACCOUNTS", "")

        # Engagement thresholds (viral detection)
        social_fb_reaction_threshold = int(os.getenv("SOCIAL_FB_REACTION_THRESHOLD", "10"))
        social_ig_comment_threshold = int(os.getenv("SOCIAL_IG_COMMENT_THRESHOLD", "5"))
        social_twitter_mention_threshold = int(os.getenv("SOCIAL_TWITTER_MENTION_THRESHOLD", "3"))

        # Daily summary generation time (default: 18:00 = 6:00 PM)
        social_summary_time = os.getenv("SOCIAL_SUMMARY_TIME", "18:00")

        # Platform-specific enable/disable (default: all enabled)
        social_facebook_enabled = os.getenv("SOCIAL_FACEBOOK_ENABLED", "true").lower() in ("true", "1", "yes")
        social_instagram_enabled = os.getenv("SOCIAL_INSTAGRAM_ENABLED", "true").lower() in ("true", "1", "yes")
        social_twitter_enabled = os.getenv("SOCIAL_TWITTER_ENABLED", "true").lower() in ("true", "1", "yes")

        # =============================================================================
        # GOLD TIER: Social Media Posting
        # =============================================================================
        # Directory for social media browser sessions
        social_session_dir = os.getenv("SOCIAL_SESSION_DIR", ".social_session")

        # Chrome DevTools Protocol ports for each platform
        social_fb_cdp_port = int(os.getenv("SOCIAL_FB_CDP_PORT", "9223"))
        social_ig_cdp_port = int(os.getenv("SOCIAL_IG_CDP_PORT", "9224"))
        social_tw_cdp_port = int(os.getenv("SOCIAL_TW_CDP_PORT", "9225"))

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            raise ValueError(f"Invalid LOG_LEVEL: {log_level}. Must be one of {valid_log_levels}")

        return cls(
            vault_root=vault_root,
            gmail_credentials_file=gmail_credentials_file,
            gmail_token_file=gmail_token_file,
            gmail_scopes=gmail_scopes,
            linkedin_access_token=linkedin_access_token,
            linkedin_person_urn=linkedin_person_urn,
            whatsapp_session_dir=whatsapp_session_dir,
            whatsapp_cdp_port=whatsapp_cdp_port,
            whatsapp_headless=whatsapp_headless,
            dry_run=dry_run,
            log_level=log_level,
            check_interval=check_interval,
            orchestrator_check_interval=orchestrator_check_interval,
            # Gold Tier: Social Media Monitoring
            social_watcher_enabled=social_watcher_enabled,
            social_watcher_interval=social_watcher_interval,
            social_high_priority_keywords=social_high_priority_keywords,
            social_business_keywords=social_business_keywords,
            social_whitelist_accounts=social_whitelist_accounts,
            social_fb_reaction_threshold=social_fb_reaction_threshold,
            social_ig_comment_threshold=social_ig_comment_threshold,
            social_twitter_mention_threshold=social_twitter_mention_threshold,
            social_summary_time=social_summary_time,
            social_facebook_enabled=social_facebook_enabled,
            social_instagram_enabled=social_instagram_enabled,
            social_twitter_enabled=social_twitter_enabled,
            # Gold Tier: Social Media Posting
            social_session_dir=social_session_dir,
            social_fb_cdp_port=social_fb_cdp_port,
            social_ig_cdp_port=social_ig_cdp_port,
            social_tw_cdp_port=social_tw_cdp_port,
        )

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If required settings are invalid or missing
            FileNotFoundError: If required files don't exist

        Example:
            >>> config = Config.load_from_env()
            >>> config.validate()
        """
        # Check vault root exists
        if not self.vault_root.exists():
            raise FileNotFoundError(f"Vault root not found: {self.vault_root}")

        # Check check intervals are positive
        if self.check_interval <= 0:
            raise ValueError("CHECK_INTERVAL must be positive")

        if self.orchestrator_check_interval <= 0:
            raise ValueError("ORCHESTRATOR_CHECK_INTERVAL must be positive")

        # Check WhatsApp CDP port is valid
        if not (1024 <= self.whatsapp_cdp_port <= 65535):
            raise ValueError("WHATSAPP_CDP_PORT must be between 1024 and 65535")

        # Validate social media watcher settings
        if self.social_watcher_interval <= 0:
            raise ValueError("SOCIAL_WATCHER_INTERVAL must be positive")

        if self.social_fb_reaction_threshold <= 0:
            raise ValueError("SOCIAL_FB_REACTION_THRESHOLD must be positive")

        if self.social_ig_comment_threshold <= 0:
            raise ValueError("SOCIAL_IG_COMMENT_THRESHOLD must be positive")

        if self.social_twitter_mention_threshold <= 0:
            raise ValueError("SOCIAL_TWITTER_MENTION_THRESHOLD must be positive")

        # Validate social summary time format (HH:MM)
        try:
            datetime.strptime(self.social_summary_time, "%H:%M")
        except ValueError:
            raise ValueError("SOCIAL_SUMMARY_TIME must be in HH:MM format (e.g., 18:00)")

        # Validate social media CDP ports
        if not (1024 <= self.social_fb_cdp_port <= 65535):
            raise ValueError("SOCIAL_FB_CDP_PORT must be between 1024 and 65535")

        if not (1024 <= self.social_ig_cdp_port <= 65535):
            raise ValueError("SOCIAL_IG_CDP_PORT must be between 1024 and 65535")

        if not (1024 <= self.social_tw_cdp_port <= 65535):
            raise ValueError("SOCIAL_TW_CDP_PORT must be between 1024 and 65535")


# Global config instance (loaded on first import)
_config: Config | None = None


def get_config() -> Config:
    """
    Get global config instance (singleton pattern).

    Returns:
        Config instance

    Example:
        >>> from my_ai_employee.config import get_config
        >>> config = get_config()
        >>> config.dry_run
        True
    """
    global _config
    if _config is None:
        _config = Config.load_from_env()
    return _config


def reload_config() -> Config:
    """
    Reload configuration from environment (useful for testing).

    Returns:
        Reloaded Config instance

    Example:
        >>> os.environ["DRY_RUN"] = "false"
        >>> config = reload_config()
        >>> config.dry_run
        False
    """
    global _config
    _config = Config.load_from_env()
    return _config
