import pytest
import asyncio
import time
from app.reliability.circuit_breaker import CircuitBreaker, CircuitState

@pytest.mark.asyncio
async def test_circuit_breaker_basic_flow():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1, name="test")
    
    # Success case
    async def success_fn():
        return "ok"
    
    assert await cb.call(success_fn) == "ok"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1, name="test")
    
    async def fail_fn():
        raise ValueError("fail")
    
    # First failure
    with pytest.raises(ValueError):
        await cb.call(fail_fn)
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 1
    
    # Second failure -> Open
    with pytest.raises(ValueError):
        await cb.call(fail_fn)
    assert cb.state == CircuitState.OPEN
    assert cb.failure_count == 2
    
    # Immediate call should fail with Exception (Circuit OPEN)
    with pytest.raises(Exception, match="OPEN"):
        await cb.call(fail_fn)

@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.5, name="test")
    
    async def fail_fn():
        raise ValueError("fail")
        
    async def success_fn():
        return "recovered"

    # Open the circuit
    with pytest.raises(ValueError):
        await cb.call(fail_fn)
    assert cb.state == CircuitState.OPEN
    
    # Wait for recovery timeout
    await asyncio.sleep(0.6)
    
    # Half-open and recover
    assert await cb.call(success_fn) == "recovered"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

@pytest.mark.asyncio
async def test_circuit_breaker_timeout_enforcement():
    # 0.1s execution timeout
    cb = CircuitBreaker(execution_timeout=0.1, name="test-timeout")
    
    async def slow_fn():
        await asyncio.sleep(0.5)
        return "too late"
        
    with pytest.raises(asyncio.TimeoutError):
        await cb.call(slow_fn)
    
    assert cb.failure_count == 1
