import pytest
from agents.may import MayAgent
from agents.models import AgentRole


def test_may_initialization(mock_anthropic_client):
    """MayAgent 초기화 검증."""
    agent = MayAgent()
    assert agent.name == "may"
    assert agent.role == AgentRole.REVIEWER


def test_may_review_with_code_only(mock_anthropic_client):
    """코드만으로 review()가 동작하는지 확인."""
    agent = MayAgent()
    result = agent.review("def foo(): pass")
    assert result.success is True
    assert "def foo(): pass" in agent.history[0].content


def test_may_review_with_all_params(mock_anthropic_client):
    """코드+테스트+요구사항 모두 포함하는지 확인."""
    agent = MayAgent()
    result = agent.review(
        code="def add(a, b): return a + b",
        tests="def test_add(): assert add(1,2)==3",
        requirements="덧셈 함수 구현",
    )
    user_prompt = agent.history[0].content
    assert "def add(a, b): return a + b" in user_prompt
    assert "def test_add(): assert add(1,2)==3" in user_prompt
    assert "덧셈 함수 구현" in user_prompt


def test_may_system_prompt_contains_approved(mock_anthropic_client):
    """system_prompt에 APPROVED 형식이 언급되어야 함."""
    agent = MayAgent()
    assert "APPROVED" in agent.system_prompt
