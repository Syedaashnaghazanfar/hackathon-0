#!/usr/bin/env python3
"""
Unified Watcher Runner - Run any watcher or all watchers together.

Usage:
    # Run filesystem watcher (Bronze tier - default)
    python run_watcher.py
    python run_watcher.py --watcher filesystem

    # Run Gmail watcher (Silver tier)
    python run_watcher.py --watcher gmail

    # Run all watchers with orchestration (Silver tier)
    python run_watcher.py --watcher all

    # Run specific watchers
    python run_watcher.py --watcher gmail,linkedin

Environment variables (from .env):
    VAULT_ROOT: Path to Obsidian vault root
    WATCH_FOLDER: Path to folder to watch for new files (filesystem only)
    WATCH_MODE: "events" or "polling" (default: events)
    WATCHER_CHECK_INTERVAL: Seconds between health checks (default: 30)
    LOG_LEVEL: Logging level (default: INFO)
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the watcher."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run AI Employee watchers (Bronze & Silver tier)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bronze Tier - Filesystem watcher only
  python run_watcher.py
  python run_watcher.py --watcher filesystem

  # Silver Tier - Individual watchers
  python run_watcher.py --watcher gmail
  python run_watcher.py --watcher linkedin
  python run_watcher.py --watcher whatsapp

  # Silver Tier - All watchers with orchestration
  python run_watcher.py --watcher all

  # Silver Tier - Specific watchers
  python run_watcher.py --watcher gmail,linkedin

  # Override configuration
  python run_watcher.py --watcher filesystem --vault-path ./vault --watch-folder ./watch
        """
    )

    parser.add_argument(
        '--watcher',
        type=str,
        default='filesystem',
        help='Watcher to run: filesystem, gmail, linkedin, whatsapp, all, or comma-separated list (default: filesystem)'
    )

    parser.add_argument(
        '--vault-path',
        type=str,
        help='Path to Obsidian vault root (overrides VAULT_ROOT env var)'
    )

    parser.add_argument(
        '--watch-folder',
        type=str,
        help='Path to folder to watch for new files (filesystem only, overrides WATCH_FOLDER env var)'
    )

    parser.add_argument(
        '--watch-mode',
        type=str,
        choices=['events', 'polling'],
        help='Watch mode for filesystem: "events" or "polling" (overrides WATCH_MODE env var)'
    )

    parser.add_argument(
        '--check-interval',
        type=int,
        help='Seconds between checks (default: 60 for filesystem, 30 for others)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (overrides LOG_LEVEL env var)'
    )

    return parser.parse_args()


def load_config(args: argparse.Namespace) -> dict:
    """Load configuration from .env and command-line arguments."""
    config = {
        'watcher': args.watcher.lower(),
        'vault_path': args.vault_path or os.getenv('VAULT_ROOT', 'AI_Employee_Vault'),
        'watch_folder': args.watch_folder or os.getenv('WATCH_FOLDER', 'test_watch_folder'),
        'watch_mode': args.watch_mode or os.getenv('WATCH_MODE', 'events'),
        'check_interval': args.check_interval or int(os.getenv('WATCHER_CHECK_INTERVAL', '60')),
        'log_level': args.log_level or os.getenv('LOG_LEVEL', 'INFO')
    }

    # Convert paths to Path objects
    config['vault_path'] = Path(config['vault_path']).resolve()
    config['watch_folder'] = Path(config['watch_folder']).resolve()

    return config


def run_filesystem_watcher(config: dict) -> int:
    """Run filesystem watcher (Bronze tier)."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Bronze Tier - Filesystem Watcher")
    logger.info("=" * 60)
    logger.info(f"Vault: {config['vault_path']}")
    logger.info(f"Watch folder: {config['watch_folder']}")
    logger.info(f"Watch mode: {config['watch_mode']}")
    logger.info(f"Check interval: {config['check_interval']}s")
    logger.info("=" * 60)

    # Validate paths
    if not config['vault_path'].exists():
        logger.error(f"Vault path does not exist: {config['vault_path']}")
        return 1

    if not config['watch_folder'].exists():
        logger.error(f"Watch folder does not exist: {config['watch_folder']}")
        return 1

    # Import and run watcher
    from watchers.filesystem_watcher import FilesystemWatcher

    watcher = FilesystemWatcher(
        vault_path=str(config['vault_path']),
        watch_folder=str(config['watch_folder']),
        watch_mode=config['watch_mode'],
        check_interval=config['check_interval']
    )

    watcher.run()
    return 0


def run_gmail_watcher(config: dict) -> int:
    """Run Gmail watcher (Silver tier)."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Silver Tier - Gmail Watcher")
    logger.info("=" * 60)
    logger.info(f"Vault: {config['vault_path']}")
    logger.info(f"Check interval: {config['check_interval']}s")
    logger.info("=" * 60)

    # Import and run watcher
    from watchers.gmail_watcher import GmailWatcher

    watcher = GmailWatcher(
        vault_path=str(config['vault_path']),
        check_interval=config['check_interval']
    )

    watcher.run()
    return 0


def run_linkedin_watcher(config: dict) -> int:
    """Run LinkedIn watcher (Silver tier)."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Silver Tier - LinkedIn Watcher")
    logger.info("=" * 60)
    logger.info(f"Vault: {config['vault_path']}")
    logger.info(f"Check interval: {config['check_interval']}s")
    logger.info("=" * 60)

    # Import and run watcher
    from watchers.linkedin_watcher import LinkedInWatcher

    watcher = LinkedInWatcher(
        vault_path=str(config['vault_path']),
        check_interval=config['check_interval']
    )

    watcher.run()
    return 0


def run_whatsapp_watcher(config: dict) -> int:
    """Run WhatsApp watcher (Silver tier)."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Silver Tier - WhatsApp Watcher")
    logger.info("=" * 60)
    logger.info(f"Vault: {config['vault_path']}")
    logger.info(f"Check interval: {config['check_interval']}s")
    logger.info("=" * 60)

    # Import and run watcher
    from watchers.whatsapp_watcher import WhatsAppWatcher

    watcher = WhatsAppWatcher(
        vault_path=str(config['vault_path']),
        check_interval=config['check_interval']
    )

    watcher.run()
    return 0


def run_all_watchers(config: dict) -> int:
    """Run all watchers with orchestration (Silver tier)."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Silver Tier - All Watchers (Orchestrated)")
    logger.info("=" * 60)
    logger.info(f"Vault: {config['vault_path']}")
    logger.info(f"Health check interval: {config['check_interval']}s")
    logger.info("=" * 60)

    # Import and run orchestrator
    from orchestrate_watchers import MultiWatcherOrchestrator

    orchestrator = MultiWatcherOrchestrator()
    orchestrator.start()
    return 0


def main() -> int:
    """Main entrypoint for the watcher runner."""
    try:
        # Parse arguments
        args = parse_args()

        # Load configuration
        config = load_config(args)

        # Setup logging
        setup_logging(config['log_level'])
        logger = logging.getLogger(__name__)

        # Parse watcher selection
        watcher_type = config['watcher']

        # Route to appropriate watcher
        if watcher_type == 'filesystem':
            return run_filesystem_watcher(config)

        elif watcher_type == 'gmail':
            return run_gmail_watcher(config)

        elif watcher_type == 'linkedin':
            return run_linkedin_watcher(config)

        elif watcher_type == 'whatsapp':
            return run_whatsapp_watcher(config)

        elif watcher_type == 'all':
            return run_all_watchers(config)

        elif ',' in watcher_type:
            # Multiple watchers specified
            logger.error("Running multiple specific watchers not yet implemented")
            logger.error("Use --watcher all to run all watchers with orchestration")
            return 1

        else:
            logger.error(f"Unknown watcher type: {watcher_type}")
            logger.error("Valid options: filesystem, gmail, linkedin, whatsapp, all")
            return 1

    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("\nWatcher stopped by user")
        return 0

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
