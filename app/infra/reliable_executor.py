import time
from app.infra.logger import (
    TOOL_EXECUTION_COUNTER,
    TOOL_EXECUTION_LATENCY,
)


class ReliableExecutor:
    """
    Wraps tool execution with:
    - Timeout control
    - Retry policy
    - Structured error formatting
    - Metrics instrumentation
    """

    def __init__(self, retry_policy, timeout_executor):
        self.retry_policy = retry_policy
        self.timeout_executor = timeout_executor

    def execute(self, tool, step):

        tool_name = step.get("tool", "unknown")
        start_time = time.time()

        try:
            result = self.retry_policy.execute(
                self.timeout_executor.execute,
                tool.execute,
                step
            )

            latency = time.time() - start_time

            TOOL_EXECUTION_COUNTER.labels(
                tool_name=tool_name,
                status="success"
            ).inc()

            TOOL_EXECUTION_LATENCY.labels(
                tool_name=tool_name
            ).observe(latency)

            result.setdefault("metadata", {})
            result["metadata"]["total_execution_time"] = latency
            result["metadata"]["status"] = "success"

            return result

        except Exception as e:
            latency = time.time() - start_time

            TOOL_EXECUTION_COUNTER.labels(
                tool_name=tool_name,
                status="failure"
            ).inc()

            TOOL_EXECUTION_LATENCY.labels(
                tool_name=tool_name
            ).observe(latency)

            return {
                "status": "error",
                "data": None,
                "metadata": {
                    "error": str(e),
                    "total_execution_time": latency,
                }
            }
