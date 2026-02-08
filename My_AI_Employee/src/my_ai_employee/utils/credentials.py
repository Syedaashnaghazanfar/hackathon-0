"""
Credential management for AI Employee services.

Stores and retrieves sensitive credentials using keyring or environment fallback.
Never logs actual credentials to output.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CredentialManager:
    """Manage credentials for external services."""

    def __init__(self, service_name: str):
        """
        Initialize credential manager.

        Args:
            service_name: Name of the service (e.g., "ai_employee_odoo")
        """
        self.service_name = service_name

    def store(self, key: str, value: str) -> bool:
        """
        Store credential in keyring.

        Args:
            key: Credential key (e.g., "odoo_api_key")
            value: Credential value

        Returns:
            True if stored successfully
        """
        try:
            # For now, just set environment variable
            # In production, use keyring module
            os.environ[f"{self.service_name}_{key}".upper()] = value
            logger.info(f"Credential '{key}' stored for {self.service_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to store credential '{key}': {e}")
            return False

    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve credential from keyring or environment.

        Args:
            key: Credential key (e.g., "odoo_api_key")

        Returns:
            Credential value or None if not found
        """
        # Try environment variable first
        env_key = f"{self.service_name}_{key}".upper()
        value = os.getenv(env_key)
        if value:
            return value

        # Try direct key (for backwards compatibility)
        direct_key = key.upper()
        value = os.getenv(direct_key)
        if value:
            return value

        logger.warning(f"Credential '{key}' not found for {self.service_name}")
        return None

    def delete(self, key: str) -> bool:
        """
        Delete credential from keyring.

        Args:
            key: Credential key

        Returns:
            True if deleted successfully
        """
        try:
            env_key = f"{self.service_name}_{key}".upper()
            if env_key in os.environ:
                del os.environ[env_key]
                logger.info(f"Credential '{key}' deleted for {self.service_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete credential '{key}': {e}")
            return False
