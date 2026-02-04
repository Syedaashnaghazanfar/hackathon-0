"""
Logging configuration utility for Silver Tier AI Employee.

Provides structured logging setup for watchers, MCP servers, and orchestrator.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    logger_name: str,
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Setup structured logging for a component.

    Args:
        logger_name: Name of the logger (e.g., "gmail_watcher", "orchestrator")
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to INFO.
        log_file: Optional log file path. If provided, logs to both console and file.

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging("gmail_watcher", log_level="DEBUG")
        >>> logger.info("Gmail watcher started")
    """
    # Get log level from environment or parameter
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")

    # Create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_heartbeat(logger: logging.Logger, component: str) -> None:
    """
    Log heartbeat message for health monitoring.

    Args:
        logger: Logger instance
        component: Component name (e.g., "gmail_watcher")

    Example:
        >>> logger = setup_logging("gmail_watcher")
        >>> log_heartbeat(logger, "gmail_watcher")
    """
    logger.info(f"[HEARTBEAT] {component} is running")


def log_action_item_created(
    logger: logging.Logger, action_id: str, source: str, priority: str
) -> None:
    """
    Log action item creation.

    Args:
        logger: Logger instance
        action_id: Unique action item identifier
        source: Source type (email, whatsapp, linkedin, file_drop)
        priority: Priority level (high, medium, low)

    Example:
        >>> logger = setup_logging("gmail_watcher")
        >>> log_action_item_created(logger, "20260122-150000-gmail-abc123", "email", "high")
    """
    logger.info(
        f"[ACTION_ITEM_CREATED] action_id={action_id}, source={source}, priority={priority}"
    )


def log_execution_result(
    logger: logging.Logger,
    action_id: str,
    tool_name: str,
    status: str,
    error: Optional[str] = None,
) -> None:
    """
    Log execution result.

    Args:
        logger: Logger instance
        action_id: Unique action item identifier
        tool_name: MCP tool name (send_email, publish_post, send_whatsapp_message)
        status: Execution status (success, failed, dry_run)
        error: Optional error message

    Example:
        >>> logger = setup_logging("orchestrator")
        >>> log_execution_result(logger, "action_123", "send_email", "success")
    """
    if error:
        logger.error(
            f"[EXECUTION] action_id={action_id}, tool={tool_name}, status={status}, error={error}"
        )
    else:
        logger.info(
            f"[EXECUTION] action_id={action_id}, tool={tool_name}, status={status}"
        )


def log_dry_run_mode(logger: logging.Logger, component: str) -> None:
    """
    Log warning about dry-run mode.

    Args:
        logger: Logger instance
        component: Component name

    Example:
        >>> logger = setup_logging("orchestrator")
        >>> log_dry_run_mode(logger, "orchestrator")
    """
    logger.warning(
        f"[DRY_RUN] {component} is running in DRY-RUN mode. No real actions will be executed."
    )
