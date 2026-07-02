import asyncio
import logging


class RetryPolicy:
    """
    Generic retry policy with exponential backoff for async operations.
    """

    def __init__(self, max_retries=2, base_delay=0.5, backoff_factor=2):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor

    async def execute(self, func, *args, **kwargs):
        """
        Executes a callable (sync or async) with retry logic.
        """

        attempt = 0
        delay = self.base_delay

        while attempt <= self.max_retries:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    # Handle both sync and async functions correctly
                    res = func(*args, **kwargs)
                    if asyncio.iscoroutine(res):
                        return await res
                    return res

            except Exception as e:
                if attempt >= self.max_retries:
                    raise

                logging.warning(
                    f"[RetryPolicy] Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay}s..."
                )

                await asyncio.sleep(delay)
                delay *= self.backoff_factor
                attempt += 1
