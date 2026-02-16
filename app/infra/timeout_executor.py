import concurrent.futures
import logging


class TimeoutExecutor:
    """
    Executes a function with a timeout constraint.
    """

    def __init__(self, timeout_seconds=10):
        self.timeout_seconds = timeout_seconds

    def execute(self, func, *args, **kwargs):

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)

            try:
                return future.result(timeout=self.timeout_seconds)

            except concurrent.futures.TimeoutError:
                logging.error(
                    f"[TimeoutExecutor] Execution exceeded "
                    f"{self.timeout_seconds} seconds."
                )
                raise TimeoutError(
                    f"Execution timed out after {self.timeout_seconds} seconds."
                )
