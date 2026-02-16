import time
import logging


class RetryPolicy:
    """
    Generic retry policy with exponential backoff.
    """

    def __init__(self, max_retries=2, base_delay=0.5, backoff_factor=2):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor

    def execute(self, func, *args, **kwargs):
        """
        Executes a function with retry logic.
        """

        attempt = 0
        delay = self.base_delay

        while attempt <= self.max_retries:
            try:
                return func(*args, **kwargs)

            except Exception as e:
                if attempt >= self.max_retries:
                    raise

                logging.warning(
                    f"[RetryPolicy] Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay}s..."
                )

                time.sleep(delay)
                delay *= self.backoff_factor
                attempt += 1
