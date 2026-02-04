#!/usr/bin/env python3
"""
Initialize Obsidian vault structure for Silver Tier AI Employee.

Creates all required folders for the Silver tier approval workflow and audit logging.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from my_ai_employee.utils import ensure_folder_structure, get_vault_root


def main():
    """Initialize vault structure for Silver tier."""
    print("Initializing Obsidian vault structure for Silver Tier AI Employee...")

    # Check vault root
    try:
        vault_root = get_vault_root()
        print(f"Vault root: {vault_root}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("\nPlease create the vault directory or set VAULT_ROOT environment variable.")
        sys.exit(1)

    # Ensure folder structure
    ensure_folder_structure()

    # Verify folders
    folders = [
        "Needs_Action",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Failed",
        "Done",
        "Logs",
        "Plans",
    ]

    print("\nCreated/verified folders:")
    for folder in folders:
        folder_path = vault_root / folder
        status = "✓" if folder_path.exists() else "✗"
        print(f"  {status} {folder}")

    print("\n✓ Vault structure initialized successfully!")
    print("\nNext steps:")
    print("  1. Update Company_Handbook.md with approval thresholds")
    print("  2. Configure .env file with credentials")
    print("  3. Run setup scripts for Gmail, LinkedIn, and WhatsApp authentication")


if __name__ == "__main__":
    main()
