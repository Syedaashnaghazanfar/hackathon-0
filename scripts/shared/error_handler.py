#!/usr/bin/env python3
"""
Shared error handling utility for Gold Tier AI Employee.

Provides exponential backoff decorator for retry logic with configurable
max retries and delays. Used across all Gold tier features for resilience.
"""

import functools
import logging
import time
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)

    Retries on: TimeoutError, HTTPError, ConnectionError, OSError

    Exponential backoff: base_delay * (2 ** attempt_number)
    - Attempt 0: Immediate (no delay)
    - Attempt 1: base_delay * 2^0 = 1s
    - Attempt 2: base_delay * 2^1 = 2s
    - Attempt 3: base_delay * 2^2 = 4s

    Example:
        @retry_with_backoff(max_retries=3, base_delay=1.0)
        def api_call():
            # Will retry up to 3 times with 1s, 2s, 4s delays
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, ConnectionError, OSError) as e:
                    last_exception = e

                    # If this is the last attempt, raise the exception
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)

            # This should never be reached, but mypy needs it
            raise last_exception  # type: ignore

        return wrapper
    return decorator


def safe_default(value: Any, default: Any) -> Any:
    """
    Return default value if value is None or raises exception.

    Args:
        value: Value to check
        default: Default value to return if value is invalid

    Returns:
        value if valid, otherwise default
    """
    try:
        if value is None:
            return default
        return value
    except Exception:
        return default


if __name__ == "__main__":
    # Test the decorator
    import random

    @retry_with_backoff(max_retries=3, base_delay=0.1)
    def test_function():
        # Simulate flaky function
        if random.random() < 0.7:
            raise ConnectionError("Simulated connection error")
        return "Success"

    # This should eventually succeed
    result = test_function()
    print(f"Result: {result}")
