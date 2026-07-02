import pytest
from app.security.policy_engine import PolicyEngine, PolicyViolationError

@pytest.fixture
def policy():
    return PolicyEngine(allowed_tools=["rag_search", "web_search"])

def test_policy_validate_plan_success(policy):
    steps = [
        {"tool": "rag_search", "query": "test query"},
        {"tool": "web_search", "query": "another query"}
    ]
    policy.validate_plan(steps)  # Should not raise

def test_policy_validate_plan_unauthorized_tool(policy):
    steps = [
        {"tool": "secret_tool", "query": "leak data"}
    ]
    with pytest.raises(PolicyViolationError, match="Unauthorized tool"):
        policy.validate_plan(steps)

def test_policy_validate_plan_too_many_steps(policy):
    steps = [{"tool": "rag_search", "query": "q"}] * 7
    with pytest.raises(PolicyViolationError, match="exceeds maximum step limit"):
        policy.validate_plan(steps)

def test_policy_validate_output_detection(policy):
    sensitive_text = "My api_key=sk-1234567890abcdef1234567890abcdef1234567890abcdef"
    with pytest.raises(PolicyViolationError, match="sensitive data pattern detected"):
        policy.validate_output(sensitive_text)

def test_policy_redact(policy):
    text = "Here is my secret ghp_123456789012345678901234567890123456 and my password=supersecret"
    redacted = policy.redact(text)
    assert "ghp_" not in redacted
    assert "password=" not in redacted
    assert "[REDACTED]" in redacted
    assert redacted.count("[REDACTED]") == 2

def test_policy_redact_no_match(policy):
    text = "This is a clean string."
    assert policy.redact(text) == text
