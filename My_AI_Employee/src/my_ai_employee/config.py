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
