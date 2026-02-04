"""
Retry utility for Silver Tier AI Employee.

Provides exponential backoff retry logic for MCP server calls and watcher operations.
"""

import time
import logging
from typing import Callable, Any, Optional, Type
from functools import wraps


logger = logging.getLogger(__name__)


def exponential_backoff_retry(
    max_retries: int = 3,
    backoff_seconds: list[int] = None,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator for exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_seconds: List of backoff delays in seconds (default: [1, 2, 4])
        exceptions: Tuple of exception types to catch and retry (default: all exceptions)

    Returns:
        Decorated function with retry logic

    Example:
        >>> @exponential_backoff_retry(max_retries=3, backoff_seconds=[1, 2, 4])
        ... def send_email(to, subject, body):
        ...     # API call that might fail
        ...     pass
    """
    if backoff_seconds is None:
        backoff_seconds = [1, 2, 4]

    if len(backoff_seconds) != max_retries:
        raise ValueError(f"backoff_seconds length ({len(backoff_seconds)}) must equal max_retries ({max_retries})")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    retry_num = attempt + 1

                    if retry_num < max_retries:
                        delay = backoff_seconds[attempt]
                        logger.warning(
                            f"{func.__name__} failed (attempt {retry_num}/{max_retries}): {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {e}"
                        )

            # All retries exhausted
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    backoff_seconds: list[int] = None,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
) -> Any:
    """
    Retry a function call with exponential backoff (non-decorator version).

    Args:
        func: Function to call
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_seconds: List of backoff delays in seconds (default: [1, 2, 4])
        exceptions: Tuple of exception types to catch and retry (default: all exceptions)

    Returns:
        Function return value

    Raises:
        Last exception if all retries fail

    Example:
        >>> def send_email():
        ...     # API call that might fail
        ...     pass
        >>> result = retry_with_backoff(send_email, max_retries=3)
    """
    if backoff_seconds is None:
        backoff_seconds = [1, 2, 4]

    if len(backoff_seconds) != max_retries:
        raise ValueError(f"backoff_seconds length ({len(backoff_seconds)}) must equal max_retries ({max_retries})")

    last_exception = None

    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            retry_num = attempt + 1

            if retry_num < max_retries:
                delay = backoff_seconds[attempt]
                logger.warning(
                    f"{func.__name__} failed (attempt {retry_num}/{max_retries}): {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"{func.__name__} failed after {max_retries} attempts: {e}"
                )

    # All retries exhausted
    if last_exception:
        raise last_exception
