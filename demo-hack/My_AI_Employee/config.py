"""
Centralized configuration management for Bronze Tier AI Employee.

Loads configuration from environment variables and provides defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


# Load .env file if it exists
load_dotenv()


class Config:
    """
    Configuration settings for Bronze Tier AI Employee.

    All settings can be overridden via environment variables.
    """

    # Vault Configuration
    VAULT_PATH: Path = Path(os.getenv('VAULT_PATH', 'My_AI_Employee/AI_Employee_Vault'))

    # Watcher Configuration
    WATCH_FOLDER: Path = Path(os.getenv('WATCH_FOLDER', 'watch_folder'))
    WATCH_MODE: str = os.getenv('WATCH_MODE', 'events')  # 'events' or 'polling'
    CHECK_INTERVAL: int = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    # Dedupe Configuration
    DEDUPE_STATE_FILE: Path = Path(os.getenv('DEDUPE_STATE_FILE', 'dedupe_state.json'))

    # System Configuration
    MAX_RECENT_ACTIVITIES: int = int(os.getenv('MAX_RECENT_ACTIVITIES', '10'))
    MAX_FILENAME_LENGTH: int = int(os.getenv('MAX_FILENAME_LENGTH', '50'))

    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration settings.

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        # Validate watch mode
        if cls.WATCH_MODE not in ['events', 'polling']:
            errors.append(f"Invalid WATCH_MODE: {cls.WATCH_MODE}. Must be 'events' or 'polling'")

        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL.upper() not in valid_log_levels:
            errors.append(f"Invalid LOG_LEVEL: {cls.LOG_LEVEL}. Must be one of {valid_log_levels}")

        # Validate numeric values
        if cls.CHECK_INTERVAL <= 0:
            errors.append(f"CHECK_INTERVAL must be positive, got: {cls.CHECK_INTERVAL}")

        if cls.MAX_RECENT_ACTIVITIES <= 0:
            errors.append(f"MAX_RECENT_ACTIVITIES must be positive, got: {cls.MAX_RECENT_ACTIVITIES}")

        is_valid = len(errors) == 0
        return is_valid, errors

    @classmethod
    def get_summary(cls) -> dict:
        """
        Get a summary of current configuration.

        Returns:
            Dictionary with configuration summary
        """
        return {
            'vault_path': str(cls.VAULT_PATH),
            'watch_folder': str(cls.WATCH_FOLDER),
            'watch_mode': cls.WATCH_MODE,
            'check_interval': cls.CHECK_INTERVAL,
            'log_level': cls.LOG_LEVEL,
            'dedupe_state_file': str(cls.DEDUPE_STATE_FILE)
        }


# Create a singleton instance
config = Config()
