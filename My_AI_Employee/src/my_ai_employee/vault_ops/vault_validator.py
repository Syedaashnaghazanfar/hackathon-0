"""
Vault structure validator for Silver Tier AI Employee.

Validates that the Obsidian vault has all required folders and files.
"""

from pathlib import Path
from typing import List, Tuple
import logging

from my_ai_employee.config import get_config


logger = logging.getLogger(__name__)


def validate_vault_structure() -> Tuple[bool, List[str]]:
    """
    Validate vault structure on startup.

    Checks for:
    - Vault root exists
    - All required Silver tier folders exist
    - Required Bronze tier folders exist (backward compatibility)
    - Company_Handbook.md exists

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> is_valid, errors = validate_vault_structure()
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"ERROR: {error}")
    """
    config = get_config()
    vault_root = config.vault_root
    errors = []

    # Check vault root exists
    if not vault_root.exists():
        errors.append(f"Vault root does not exist: {vault_root}")
        return False, errors

    # Required folders (Bronze + Silver tier)
    required_folders = [
        "Needs_Action",  # Bronze tier
        "Done",  # Bronze tier
        "Plans",  # Bronze tier
        "Pending_Approval",  # Silver tier
        "Approved",  # Silver tier
        "Rejected",  # Silver tier
        "Failed",  # Silver tier
        "Logs",  # Silver tier
    ]

    # Check folders
    for folder_name in required_folders:
        folder_path = vault_root / folder_name
        if not folder_path.exists():
            errors.append(f"Required folder missing: {folder_name}")

    # Check Company_Handbook.md
    handbook_path = vault_root / "Company_Handbook.md"
    if not handbook_path.exists():
        errors.append("Company_Handbook.md not found in vault root")

    # Check Dashboard.md (optional but recommended)
    dashboard_path = vault_root / "Dashboard.md"
    if not dashboard_path.exists():
        logger.warning("Dashboard.md not found in vault root (optional)")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_or_exit() -> None:
    """
    Validate vault structure and exit if invalid.

    Raises:
        SystemExit: If vault structure is invalid

    Example:
        >>> # At the start of watcher or orchestrator
        >>> validate_or_exit()
    """
    is_valid, errors = validate_vault_structure()

    if not is_valid:
        logger.error("Vault structure validation failed:")
        for error in errors:
            logger.error(f"  - {error}")

        logger.error("\nPlease run: uv run python scripts/setup/initialize_vault.py")
        raise SystemExit(1)

    logger.info("Vault structure validation passed")


def ensure_folder_exists(folder_name: str) -> Path:
    """
    Ensure a specific vault folder exists (create if missing).

    Args:
        folder_name: Name of folder to ensure (e.g., "Pending_Approval")

    Returns:
        Path to folder

    Example:
        >>> pending_path = ensure_folder_exists("Pending_Approval")
        >>> pending_path.exists()
        True
    """
    config = get_config()
    folder_path = config.vault_root / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path
