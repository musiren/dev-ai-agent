import pytest
from unittest.mock import MagicMock, patch
import anthropic

from agents.base import BaseAgent
from agents.models import AgentRole, AgentResult


class ConcreteAgent(BaseAgent):
    """테스트용 BaseAgent 구체 구현."""

    def __init__(self, **kwargs):
        super().__init__(name="test", role=AgentRole.DEVELOPER, **kwargs)

    @property
    def system_prompt(self) -> str:
        return "Test system prompt"


def test_base_agent_cannot_be_instantiated_directly():
    """BaseAgent는 abstractmethod 때문에 직접 인스턴스화 불가."""
    with pytest.raises(TypeError):
        BaseAgent(name="test", role=AgentRole.DEVELOPER)


def test_concrete_agent_initialization(mock_anthropic_client):
    """구체 에이전트 정상 초기화."""
    agent = ConcreteAgent()
    assert agent.name == "test"
    assert agent.role == AgentRole.DEVELOPER
    assert agent._history == []


def test_run_returns_agent_result(mock_anthropic_client):
    """run()이 AgentResult를 반환하는지 확인."""
    agent = ConcreteAgent()
    result = agent.run("테스트 태스크")
    assert isinstance(result, AgentResult)
    assert result.agent_name == "test"
    assert result.role == AgentRole.DEVELOPER
    assert result.success is True
    assert result.content == "테스트 응답입니다."


def test_run_adds_to_history(mock_anthropic_client):
    """run() 후 히스토리에 user/assistant 메시지가 추가되는지 확인."""
    agent = ConcreteAgent()
    agent.run("첫 번째 태스크")
    assert len(agent.history) == 2
    assert agent.history[0].role == "user"
    assert agent.history[1].role == "assistant"


def test_reset_history(mock_anthropic_client):
    """reset_history()가 히스토리를 초기화하는지 확인."""
    agent = ConcreteAgent()
    agent.run("태스크")
    assert len(agent.history) > 0
    agent.reset_history()
    assert agent.history == []


def test_run_returns_failure_on_api_error(mock_anthropic_client):
    """API 오류 시 success=False인 AgentResult를 반환하는지 확인."""
    agent = ConcreteAgent()
    mock_anthropic_client.messages.stream.side_effect = anthropic.APIConnectionError(
        request=MagicMock()
    )
    result = agent.run("태스크")
    assert result.success is False
    assert "error_type" in result.metadata
