"""Entrypoint script for running the Gmail watcher.

Usage:
    uv run python src/my_ai_employee/run_gmail_watcher.py

    # With custom check interval:
    uv run python src/my_ai_employee/run_gmail_watcher.py --check-interval 120

Configuration:
    - All settings are loaded from .env file (see .env.example)
    - Gmail OAuth credentials must be configured first
    - Run: uv run python scripts/setup/setup_gmail_oauth.py

Environment Variables (from .env):
    - VAULT_ROOT: Path to Obsidian vault
    - CHECK_INTERVAL: Seconds between checks (default: 60)
    - DRY_RUN: If true, logs actions without executing (default: true)
    - GMAIL_CREDENTIALS_FILE: Path to credentials.json
    - GMAIL_TOKEN_FILE: Path to token.json
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Import from watchers package
from my_ai_employee.watchers.gmail_watcher import GmailWatcher
from my_ai_employee.config import get_config


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the watcher.

    Args:
        verbose: Enable debug-level logging if True
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> int:
    """Main entrypoint for the Gmail watcher."""
    parser = argparse.ArgumentParser(
        description="Run the Gmail watcher for Silver AI Employee"
    )
    parser.add_argument(
        "--check-interval",
        type=int,
        default=None,
        help="Seconds between Gmail checks (overrides .env CHECK_INTERVAL)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Load config
    config = get_config()

    logger.info("=" * 60)
    logger.info("Silver AI Employee - Gmail Watcher")
    logger.info("=" * 60)
    logger.info(f"Vault Path: {config.vault_root}")
    logger.info(f"Check Interval: {args.check_interval or config.check_interval}s")
    logger.info(f"DRY_RUN mode: {config.dry_run}")
    logger.info("=" * 60)

    # Validate vault exists
    if not config.vault_root.exists():
        logger.error(f"Vault path does not exist: {config.vault_root}")
        return 1

    try:
        # Create and run watcher
        check_interval = args.check_interval or config.check_interval
        watcher = GmailWatcher(check_interval=check_interval)

        logger.info("Watcher initialized successfully")
        logger.info("Press Ctrl+C to stop watching...")
        logger.info("")

        watcher.run()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("\nWatcher stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
