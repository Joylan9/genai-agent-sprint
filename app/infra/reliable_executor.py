import time


class ReliableExecutor:
    """
    Wraps tool execution with:
    - Timeout control
    - Retry policy
    - Structured error formatting
    """

    def __init__(self, retry_policy, timeout_executor):
        self.retry_policy = retry_policy
        self.timeout_executor = timeout_executor

    def execute(self, tool, step):

        start_time = time.time()

        try:
            result = self.retry_policy.execute(
                self.timeout_executor.execute,
                tool.execute,
                step
            )

            latency = time.time() - start_time

            result.setdefault("metadata", {})
            result["metadata"]["total_execution_time"] = latency
            result["metadata"]["status"] = "success"

            return result

        except Exception as e:
            latency = time.time() - start_time

            return {
                "status": "error",
                "data": None,
                "metadata": {
                    "error": str(e),
                    "total_execution_time": latency,
                }
            }
