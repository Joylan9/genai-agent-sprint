"""
app/reliability/circuit_breaker.py

Enterprise-grade asynchronous circuit breaker
with timeout enforcement and half-open recovery.
"""

import asyncio
import time
from typing import Callable, Awaitable, Any
from enum import Enum
from datetime import datetime


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        execution_timeout: int = 15,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.execution_timeout = execution_timeout
        self.name = name

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float | None = None

        self._lock = asyncio.Lock()

    # --------------------------------------------------
    # MAIN EXECUTION WRAPPER
    # --------------------------------------------------

    async def call(self, func: Callable[[], Awaitable[Any]]) -> Any:

        async with self._lock:

            if self.state == CircuitState.OPEN:
                if not self._can_attempt_reset():
                    raise Exception(
                        f"CircuitBreaker[{self.name}] OPEN - rejecting call"
                    )
                else:
                    self.state = CircuitState.HALF_OPEN

        try:
            result = await asyncio.wait_for(
                func(),
                timeout=self.execution_timeout
            )

        except Exception as e:
            await self._record_failure()
            raise e

        await self._record_success()
        return result

    # --------------------------------------------------
    # STATE MANAGEMENT
    # --------------------------------------------------

    async def _record_failure(self):
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

    async def _record_success(self):
        async with self._lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED

    def _can_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return False

        return (
            time.time() - self.last_failure_time
        ) >= self.recovery_timeout

    # --------------------------------------------------
    # DIAGNOSTICS
    # --------------------------------------------------

    def status(self):
        return {
            "name": self.name,
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time
        }
