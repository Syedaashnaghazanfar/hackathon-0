"""
Unified multi-watcher launcher CLI for Silver Tier AI Employee.

Starts one or all watchers (Gmail, WhatsApp, LinkedIn, filesystem) based on command-line arguments.
"""

import sys
import argparse
import logging
from typing import Optional

from my_ai_employee.config import get_config
from my_ai_employee.utils import setup_logging


def main():
    """
    Main entry point for watcher launcher.

    Supports running individual watchers or all watchers simultaneously.
    """
    parser = argparse.ArgumentParser(
        description="Silver Tier AI Employee - Multi-Watcher Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Gmail watcher only
  python run_multi_watcher.py gmail

  # Run all watchers
  python run_multi_watcher.py all

  # Run filesystem watcher with custom check interval
  python run_multi_watcher.py filesystem --check-interval 30

Watchers:
  - gmail: Monitors Gmail inbox for important/unread emails
  - whatsapp: Monitors WhatsApp Web for messages (requires QR scan)
  - linkedin: Monitors LinkedIn for connection requests and messages
  - filesystem: Monitors watch folder for dropped files (Bronze tier)
  - all: Starts all configured watchers
        """
    )

    parser.add_argument(
        "watcher",
        choices=["gmail", "whatsapp", "linkedin", "filesystem", "all"],
        help="Which watcher to run"
    )

    parser.add_argument(
        "--check-interval",
        type=int,
        default=None,
        help="Check interval in seconds (overrides .env CHECK_INTERVAL)"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Log level (overrides .env LOG_LEVEL)"
    )

    args = parser.parse_args()

    # Load config
    config = get_config()

    # Override config if specified
    if args.check_interval:
        config.check_interval = args.check_interval
    if args.log_level:
        config.log_level = args.log_level

    # Setup logging
    logger = setup_logging("run_multi_watcher", log_level=config.log_level)

    logger.info(f"Starting {args.watcher} watcher(s)...")
    logger.info(f"Check interval: {config.check_interval}s")
    logger.info(f"Dry-run mode: {config.dry_run}")

    if args.watcher == "gmail":
        run_gmail_watcher(config)
    elif args.watcher == "whatsapp":
        run_whatsapp_watcher(config)
    elif args.watcher == "linkedin":
        run_linkedin_watcher(config)
    elif args.watcher == "filesystem":
        run_filesystem_watcher(config)
    elif args.watcher == "all":
        run_all_watchers(config)
    else:
        logger.error(f"Unknown watcher: {args.watcher}")
        sys.exit(1)


def run_gmail_watcher(config):
    """
    Run Gmail watcher.

    Args:
        config: Config instance
    """
    from my_ai_employee.watchers.gmail_watcher import GmailWatcher

    watcher = GmailWatcher(check_interval=config.check_interval)
    watcher.run()


def run_whatsapp_watcher(config):
    """
    Run WhatsApp watcher.

    Args:
        config: Config instance
    """
    from my_ai_employee.watchers.whatsapp_watcher import WhatsAppWatcher

    watcher = WhatsAppWatcher(check_interval=config.check_interval)
    watcher.run()


def run_linkedin_watcher(config):
    """
    Run LinkedIn watcher.

    Args:
        config: Config instance
    """
    from my_ai_employee.watchers.linkedin_watcher import LinkedInWatcher

    watcher = LinkedInWatcher(check_interval=config.check_interval)
    watcher.run()


def run_filesystem_watcher(config):
    """
    Run filesystem watcher.

    Args:
        config: Config instance
    """
    from my_ai_employee.watchers.filesystem_watcher import FilesystemWatcher

    watcher = FilesystemWatcher(
        vault_path=config.vault_root,
        watch_folder=config.watch_folder,
        watch_mode=config.watch_mode,
    )
    watcher.run()


def run_all_watchers(config):
    """
    Run all watchers in parallel using multiprocessing.

    Args:
        config: Config instance
    """
    import multiprocessing
    import signal

    logger = setup_logging("multi_watcher", log_level=config.log_level)

    # Create processes for each watcher
    processes = []

    watchers = [
        ("gmail", run_gmail_watcher),
        ("whatsapp", run_whatsapp_watcher),
        ("linkedin", run_linkedin_watcher),
        ("filesystem", run_filesystem_watcher),
    ]

    for watcher_name, watcher_func in watchers:
        process = multiprocessing.Process(
            target=watcher_func,
            args=(config,),
            name=f"{watcher_name}_watcher"
        )
        processes.append(process)
        process.start()
        logger.info(f"Started {watcher_name} watcher (PID: {process.pid})")

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        logger.info(f"Received {signal_name}, stopping all watchers...")

        for process in processes:
            if process.is_alive():
                logger.info(f"Terminating {process.name} (PID: {process.pid})")
                process.terminate()

        # Wait for all processes to finish
        for process in processes:
            process.join(timeout=10)
            if process.is_alive():
                logger.warning(f"{process.name} did not terminate, killing...")
                process.kill()

        logger.info("All watchers stopped")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info("All watchers started. Press Ctrl+C to stop.")

    # Wait for all processes
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        logger.info("Interrupted by user, stopping watchers...")
        signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main()
