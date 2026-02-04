"""
Retry logic with exponential backoff for Silver Tier AI Employee.
Implements retry strategy: immediate (0s), 25s, 7200s (2 hours).
"""

import time
import logging
from typing import Callable, Any, Optional
from datetime import datetime


class RetryHandler:
    """
    Handle retries with exponential backoff for failed actions.

    Retry schedule from constitution:
    - Attempt 1: Immediate (0 seconds)
    - Attempt 2: 25 seconds
    - Attempt 3: 7200 seconds (2 hours)

    After 3 failed attempts, action moves to Failed folder.
    """

    # Retry delays in seconds
    RETRY_DELAYS = [0, 25, 7200]  # 0s, 25s, 2h
    MAX_RETRIES = 3

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize retry handler.

        Args:
            logger: Optional logger instance for retry events
        """
        self.logger = logger or logging.getLogger(__name__)

    def execute_with_retry(
        self,
        func: Callable,
        *args,
        action_id: str = "unknown",
        **kwargs
    ) -> tuple[bool, Any, Optional[str]]:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            action_id: Identifier for logging
            **kwargs: Keyword arguments for func

        Returns:
            Tuple of (success: bool, result: Any, error: Optional[str])
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                # Apply delay before retry (except first attempt)
                if attempt > 0:
                    delay = self.RETRY_DELAYS[attempt]
                    self.logger.info(
                        f"Action {action_id}: Retry attempt {attempt + 1}/{self.MAX_RETRIES} "
                        f"after {delay}s delay"
                    )
                    time.sleep(delay)

                # Execute function
                self.logger.info(
                    f"Action {action_id}: Executing attempt {attempt + 1}/{self.MAX_RETRIES}"
                )
                result = func(*args, **kwargs)

                # Success
                self.logger.info(
                    f"Action {action_id}: Succeeded on attempt {attempt + 1}/{self.MAX_RETRIES}"
                )
                return (True, result, None)

            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    f"Action {action_id}: Failed attempt {attempt + 1}/{self.MAX_RETRIES}: {last_error}"
                )

                # If this was the last attempt, don't continue
                if attempt == self.MAX_RETRIES - 1:
                    self.logger.error(
                        f"Action {action_id}: All {self.MAX_RETRIES} attempts failed. "
                        f"Moving to Failed folder."
                    )
                    return (False, None, last_error)

        # Should never reach here, but just in case
        return (False, None, last_error)

    def should_retry(self, retry_count: int) -> bool:
        """
        Check if action should be retried based on current retry count.

        Args:
            retry_count: Current number of retry attempts

        Returns:
            True if should retry, False if max retries reached
        """
        return retry_count < self.MAX_RETRIES

    def get_next_retry_delay(self, retry_count: int) -> Optional[int]:
        """
        Get delay in seconds before next retry.

        Args:
            retry_count: Current number of retry attempts

        Returns:
            Delay in seconds, or None if max retries reached
        """
        if retry_count >= self.MAX_RETRIES:
            return None
        return self.RETRY_DELAYS[retry_count]

    def calculate_next_retry_time(self, retry_count: int) -> Optional[str]:
        """
        Calculate ISO 8601 timestamp for next retry.

        Args:
            retry_count: Current number of retry attempts

        Returns:
            ISO 8601 timestamp string, or None if max retries reached
        """
        delay = self.get_next_retry_delay(retry_count)
        if delay is None:
            return None

        next_time = datetime.utcnow().timestamp() + delay
        return datetime.fromtimestamp(next_time).isoformat() + "Z"


class RetryableError(Exception):
    """Exception that indicates an operation should be retried."""
    pass


class NonRetryableError(Exception):
    """Exception that indicates an operation should NOT be retried."""
    pass
