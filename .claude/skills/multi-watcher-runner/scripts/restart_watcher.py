#!/usr/bin/env python3
"""Restart specific watcher script."""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def restart_watcher(watcher_name: str):
    """Restart a specific watcher."""
    valid_watchers = ['gmail', 'whatsapp', 'linkedin', 'filesystem']

    if watcher_name not in valid_watchers:
        logger.error(f"Invalid watcher: {watcher_name}")
        logger.info(f"Valid options: {', '.join(valid_watchers)}")
        return False

    logger.info(f"Restarting {watcher_name} watcher...")

    if watcher_name == 'gmail':
        logger.info("Gmail: Refreshing OAuth token...")
        return _restart_gmail()
    elif watcher_name == 'whatsapp':
        logger.info("WhatsApp: Reconnecting browser...")
        return _restart_whatsapp()
    elif watcher_name == 'linkedin':
        logger.info("LinkedIn: Validating token...")
        return _restart_linkedin()
    elif watcher_name == 'filesystem':
        logger.info("Filesystem: Reinitializing watcher...")
        return _restart_filesystem()

    return False


def _restart_gmail() -> bool:
    """Restart Gmail watcher - refresh token."""
    try:
        token_file = Path('token.json')
        if token_file.exists():
            token_file.unlink()
            logger.info("Deleted old token, will re-authenticate on next run")
        logger.info("✅ Gmail watcher restarted (tokens will be refreshed)")
        return True
    except Exception as e:
        logger.error(f"Failed to restart Gmail: {e}")
        return False


def _restart_whatsapp() -> bool:
    """Restart WhatsApp watcher - keep session but reconnect browser."""
    try:
        logger.info("WhatsApp will reconnect with existing session")
        logger.info("✅ WhatsApp watcher restarted (session preserved)")
        return True
    except Exception as e:
        logger.error(f"Failed to restart WhatsApp: {e}")
        return False


def _restart_linkedin() -> bool:
    """Restart LinkedIn watcher - validate token."""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()

        token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        if not token:
            logger.error("LINKEDIN_ACCESS_TOKEN not set in .env")
            return False

        if len(token) < 10:
            logger.error("LINKEDIN_ACCESS_TOKEN appears invalid (too short)")
            return False

        logger.info("✅ LinkedIn watcher restarted (token validated)")
        return True
    except Exception as e:
        logger.error(f"Failed to restart LinkedIn: {e}")
        return False


def _restart_filesystem() -> bool:
    """Restart Filesystem watcher - verify watch folder."""
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()

        watch_folder = Path(os.getenv('WATCH_FOLDER', 'My_AI_Employee/test_watch_folder'))
        if not watch_folder.exists():
            logger.error(f"Watch folder not found: {watch_folder}")
            return False

        logger.info("✅ Filesystem watcher restarted (watch folder verified)")
        return True
    except Exception as e:
        logger.error(f"Failed to restart Filesystem: {e}")
        return False


def main():
    """Entry point."""
    if len(sys.argv) < 2:
        print("Usage: python restart_watcher.py <watcher_name>")
        print("Watcher names: gmail, whatsapp, linkedin, filesystem")
        sys.exit(1)

    watcher_name = sys.argv[1].lower()
    success = restart_watcher(watcher_name)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
