#!/usr/bin/env python3
"""
Shared environment configuration loader for Gold Tier AI Employee.

Loads and validates environment variables from .env file with support
for default values and type conversion.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Type
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Config:
    """Environment configuration manager."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            env_file: Path to .env file (default: .env in current directory)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load .env from project root
            env_path = Path('.env')
            if env_path.exists():
                load_dotenv(env_path)

        self._required_vars = set()
        self._config = {}

    def require(self, var_name: str, default: Optional[Any] = None,
              var_type: Type[T] = str) -> T:
        """
        Get required environment variable with validation.

        Args:
            var_name: Name of environment variable
            default: Default value if variable not set
            var_type: Type to convert value to

        Returns:
            Environment variable value (converted to var_type)

        Raises:
            ValueError: If required variable is not set and no default provided
        """
        value = os.getenv(var_name, default)

        if value is None:
            if default is not None:
                logger.warning(f"Environment variable {var_name} not set, using default: {default}")
                return default
            else:
                raise ValueError(f"Required environment variable {var_name} is not set")

        # Type conversion
        if var_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        else:
            return str(value)

    def get(self, var_name: str, default: Any = None) -> Any:
        """
        Get environment variable with optional default.

        Args:
            var_name: Name of environment variable
            default: Default value if not set

        Returns:
            Environment variable value or default
        """
        return os.getenv(var_name, default)

    def validate_all(self, required_vars: Dict[str, Type[T]]) -> Dict[str, Any]:
        """
        Validate all required environment variables.

        Args:
            required_vars: Dictionary of {var_name: var_type}

        Returns:
            Dictionary of validated values

        Raises:
            ValueError: If any required variable is not set
        """
        config = {}

        for var_name, var_type in required_vars.items():
            config[var_name] = self.require(var_name, var_type=var_type)

        self._config.update(config)
        return config


# Gold Tier configuration schema
GOLD_TIER_CONFIG = {
    # CEO Briefing Settings
    'BRIEFING_DAY': str,
    'BRIEFING_TIME': str,
    'BRIEFING_TIMEZONE': str,

    # Social Media Settings
    'SOCIAL_SESSION_DIR': str,
    'SOCIAL_FB_CDP_PORT': int,
    'SOCIAL_IG_CDP_PORT': int,
    'SOCIAL_TW_CDP_PORT': int,

    # Social Media Monitoring (Optional)
    'SOCIAL_WATCHER_ENABLED': bool,
    'SOCIAL_WATCHER_INTERVAL': int,
    'SOCIAL_HIGH_PRIORITY_KEYWORDS': str,
    'SOCIAL_BUSINESS_KEYWORDS': str,
    'SOCIAL_WHITELIST_ACCOUNTS': str,

    # Xero Accounting (Optional)
    'XERO_CLIENT_ID': str,
    'XERO_CLIENT_SECRET': str,
    'XERO_REDIRECT_URI': str,
    'XERO_TENANT_ID': str,
    'XERO_REFRESH_TOKEN': str,
    'XERO_WATCHER_INTERVAL': int,

    # Vault Path
    'VAULT_PATH': str,
}


def load_gold_tier_config(env_file: Optional[str] = None) -> Config:
    """
    Load and validate Gold Tier configuration.

    Args:
        env_file: Path to .env file

    Returns:
        Config instance with Gold Tier variables loaded

    Raises:
        ValueError: If required Gold Tier variables are not set
    """
    config = Config(env_file)

    # VAULT_PATH is always required
    config.require('VAULT_PATH', default='AI_Employee_Vault')

    return config


if __name__ == "__main__":
    # Test config loader
    config = load_gold_tier_config()

    # Test getting values
    try:
        vault_path = config.require('VAULT_PATH', default='AI_Employee_Vault')
        print(f"Vault path: {vault_path}")

        # Test optional value
        briefing_time = config.get('BRIEFING_TIME', default='07:00')
        print(f"Briefing time: {briefing_time}")

        # Test required value that doesn't exist (should raise error)
        # config.require('NONEXISTENT_VAR')  # This would raise ValueError

    except ValueError as e:
        print(f"Configuration error: {e}")
