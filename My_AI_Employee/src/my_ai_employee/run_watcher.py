"""Entrypoint script for running the filesystem watcher.

Usage:
    python -m my_ai_employee.run_watcher --vault-path ./AI_Employee_Vault --watch-folder ./watch_folder

Or with environment variables:
    VAULT_PATH=./AI_Employee_Vault WATCH_FOLDER=./watch_folder python -m my_ai_employee.run_watcher
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from .watchers.filesystem_watcher import FilesystemWatcher


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
    """Main entrypoint for the watcher."""
    parser = argparse.ArgumentParser(
        description="Run the filesystem watcher for Bronze AI Employee"
    )
    parser.add_argument(
        "--vault-path",
        type=str,
        default=os.getenv("VAULT_PATH", "./AI_Employee_Vault"),
        help="Path to the Obsidian vault (default: $VAULT_PATH or ./AI_Employee_Vault)",
    )
    parser.add_argument(
        "--watch-folder",
        type=str,
        default=os.getenv("WATCH_FOLDER", "./watch_folder"),
        help="Path to the folder to watch (default: $WATCH_FOLDER or ./watch_folder)",
    )
    parser.add_argument(
        "--watch-mode",
        type=str,
        choices=["events", "polling"],
        default=os.getenv("WATCH_MODE", "events"),
        help="Watch mode: 'events' (native) or 'polling' (fallback for WSL/CIFS)",
    )
    parser.add_argument(
        "--dedupe-state-file",
        type=str,
        default=os.getenv("DEDUPE_STATE_FILE", ".dedupe_state.json"),
        help="Path to dedupe state file (default: $DEDUPE_STATE_FILE or .dedupe_state.json)",
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

    # Convert paths
    vault_path = Path(args.vault_path).resolve()
    watch_folder = Path(args.watch_folder).resolve()
    dedupe_state_file = Path(args.dedupe_state_file).resolve()

    logger.info("=" * 60)
    logger.info("Bronze AI Employee - Filesystem Watcher")
    logger.info("=" * 60)
    logger.info(f"Vault Path: {vault_path}")
    logger.info(f"Watch Folder: {watch_folder}")
    logger.info(f"Watch Mode: {args.watch_mode}")
    logger.info(f"Dedupe State: {dedupe_state_file}")
    logger.info("=" * 60)

    # Validate vault exists
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        return 1

    try:
        # Create and run watcher
        watcher = FilesystemWatcher(
            vault_path=vault_path,
            watch_folder=watch_folder,
            watch_mode=args.watch_mode,
            dedupe_state_file=dedupe_state_file,
        )

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
