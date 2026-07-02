import asyncio
import logging


class TimeoutExecutor:
    """
    Executes a function with a timeout constraint in an async context.
    """

    def __init__(self, timeout_seconds=10):
        self.timeout_seconds = timeout_seconds

    async def execute(self, func, *args, **kwargs):
        """
        Executes a callable (sync or async) with a timeout.
        """
        try:
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.timeout_seconds
                )
            else:
                # If sync, wrap in to_thread to avoid blocking event loop
                return await asyncio.wait_for(
                    asyncio.to_thread(func, *args, **kwargs),
                    timeout=self.timeout_seconds
                )

        except asyncio.TimeoutError:
            logging.error(
                f"[TimeoutExecutor] Execution exceeded "
                f"{self.timeout_seconds} seconds."
            )
            raise TimeoutError(
                f"Execution timed out after {self.timeout_seconds} seconds."
            )
