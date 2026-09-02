from app.services.planning_agent_service import _is_tool_failure_refusal


def test_tool_failure_refusal_is_detected():
    answer = "I apologize, but since the web search failed, I do not have any information. I will not invent."

    assert _is_tool_failure_refusal(answer) is True


def test_regular_answer_is_not_tool_failure_refusal():
    assert _is_tool_failure_refusal("AIML commonly means Artificial Intelligence Markup Language.") is False
