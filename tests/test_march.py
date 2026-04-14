import pytest
from agents.march import MarchAgent
from agents.models import AgentRole


def test_march_initialization(mock_anthropic_client):
    """MarchAgent 초기화 검증."""
    agent = MarchAgent()
    assert agent.name == "march"
    assert agent.role == AgentRole.DEVELOPER


def test_march_system_prompt_excludes_tests(mock_anthropic_client):
    """system_prompt에 테스트 작성 금지 내용이 포함되어야 함."""
    agent = MarchAgent()
    assert "테스트" in agent.system_prompt
    assert "구현" in agent.system_prompt


def test_march_implement_includes_requirements(mock_anthropic_client):
    """implement()가 요구사항을 프롬프트에 포함하는지 확인."""
    agent = MarchAgent()
    result = agent.implement("스도쿠 게임을 만들어주세요")
    assert result.success is True
    # 히스토리에서 user 메시지 확인
    assert "스도쿠 게임을 만들어주세요" in agent.history[0].content


def test_march_refactor_includes_code_and_feedback(mock_anthropic_client):
    """refactor()가 코드와 피드백을 모두 프롬프트에 포함하는지 확인."""
    agent = MarchAgent()
    result = agent.refactor("def foo(): pass", "함수명을 개선하세요")
    assert result.success is True
    user_prompt = agent.history[0].content
    assert "def foo(): pass" in user_prompt
    assert "함수명을 개선하세요" in user_prompt
