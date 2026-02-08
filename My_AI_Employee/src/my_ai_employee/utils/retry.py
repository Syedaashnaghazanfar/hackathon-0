"""
Retry logic with exponential backoff for resilient operations.
"""

import logging
from typing import Callable, Type, Tuple
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    backoff_delays: Tuple[float, ...] = (1.0, 2.0, 4.0)
    retryable_exceptions: Tuple[Type[Exception], ...] = (ConnectionError, TimeoutError)
    non_retryable_exceptions: Tuple[Type[Exception], ...] = (ValueError, RuntimeError)

def retry_with_backoff(config: RetryConfig, operation_name: str = "operation"):
    """Decorator to retry function with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            for attempt in range(config.max_attempts):
                try:
                    if attempt > 0:
                        logger.info(f"Retry {attempt + 1}/{config.max_attempts} for {operation_name}")
                    return func(*args, **kwargs)
                except config.non_retryable_exceptions as e:
                    logger.error(f"Non-retryable error in {operation_name}: {e}")
                    raise
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt < config.max_attempts - 1:
                        delay = config.backoff_delays[attempt] if attempt < len(config.backoff_delays) else config.backoff_delays[-1]
                        logger.warning(f"Retryable error (attempt {attempt + 1}/{config.max_attempts}): {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"Max retries exceeded for {operation_name}: {e}")
            raise last_exception or Exception("Operation failed")
        return wrapper
    return decorator
