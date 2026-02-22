import pytest
from app.infra.logger import LLM_CALL_COUNTER, TOOL_EXECUTION_COUNTER, REQUEST_COUNTER

def test_metrics_increment():
    # Record initial values
    initial_llm = LLM_CALL_COUNTER.labels(status="success")._value.get()
    initial_tool = TOOL_EXECUTION_COUNTER.labels(tool_name="test", status="success")._value.get()
    
    # Increment
    LLM_CALL_COUNTER.labels(status="success").inc()
    TOOL_EXECUTION_COUNTER.labels(tool_name="test", status="success").inc()
    
    # Verify
    assert LLM_CALL_COUNTER.labels(status="success")._value.get() == initial_llm + 1
    assert TOOL_EXECUTION_COUNTER.labels(tool_name="test", status="success")._value.get() == initial_tool + 1

def test_request_metrics():
    initial_req = REQUEST_COUNTER._value.get()
    REQUEST_COUNTER.inc()
    assert REQUEST_COUNTER._value.get() == initial_req + 1
