import pytest
from agents.april import AprilAgent
from agents.models import AgentRole


def test_april_initialization(mock_anthropic_client):
    """AprilAgent 초기화 검증."""
    agent = AprilAgent()
    assert agent.name == "april"
    assert agent.role == AgentRole.TESTER


def test_april_write_tests_includes_code(mock_anthropic_client):
    """write_tests()가 코드를 프롬프트에 포함하는지 확인."""
    agent = AprilAgent()
    result = agent.write_tests("def add(a, b): return a + b")
    assert result.success is True
    assert "def add(a, b): return a + b" in agent.history[0].content


def test_april_write_tests_with_requirements(mock_anthropic_client):
    """requirements 파라미터도 프롬프트에 포함되는지 확인."""
    agent = AprilAgent()
    result = agent.write_tests("def add(a, b): return a + b", "엣지 케이스를 포함할 것")
    user_prompt = agent.history[0].content
    assert "엣지 케이스를 포함할 것" in user_prompt


def test_april_write_tests_without_requirements(mock_anthropic_client):
    """requirements 없이도 write_tests()가 동작하는지 확인."""
    agent = AprilAgent()
    result = agent.write_tests("def foo(): pass")
    assert result.success is True


def test_april_update_tests_includes_tests_and_changes(mock_anthropic_client):
    """update_tests()가 기존 테스트와 변경사항을 포함하는지 확인."""
    agent = AprilAgent()
    result = agent.update_tests("def test_foo(): pass", "foo가 bar로 변경됨")
    user_prompt = agent.history[0].content
    assert "def test_foo(): pass" in user_prompt
    assert "foo가 bar로 변경됨" in user_prompt
