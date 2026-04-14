import pytest
from unittest.mock import MagicMock, patch
from agents.june import JuneAgent
from agents.models import AgentRole, AgentResult


def make_approved_result(name, role):
    return AgentResult(agent_name=name, role=role, content="APPROVED", success=True)


def make_result(name, role, content="결과물"):
    return AgentResult(agent_name=name, role=role, content=content, success=True)


def test_june_initialization(mock_anthropic_client):
    """JuneAgent 초기화 및 팀 에이전트 생성 확인."""
    june = JuneAgent()
    assert june.name == "june"
    assert june.role == AgentRole.ORCHESTRATOR
    assert "march" in june.team
    assert "april" in june.team
    assert "may" in june.team


def test_june_team_property(mock_anthropic_client):
    """team 프로퍼티가 올바른 에이전트 딕셔너리를 반환하는지 확인."""
    june = JuneAgent()
    team = june.team
    assert len(team) == 3
    assert team["march"].name == "march"
    assert team["april"].name == "april"
    assert team["may"].name == "may"


def test_june_orchestrate_returns_correct_structure(mock_anthropic_client):
    """orchestrate()가 올바른 딕셔너리 구조를 반환하는지 확인."""
    june = JuneAgent(max_iterations=1)
    result = june.orchestrate("간단한 테스트 태스크")
    assert "success" in result
    assert "iterations" in result
    assert "artifacts" in result
    assert "summary" in result
    assert "history" in result
    assert "code" in result["artifacts"]
    assert "tests" in result["artifacts"]
    assert "review" in result["artifacts"]


def test_june_orchestrate_stops_on_approved(mock_anthropic_client):
    """May가 APPROVED 반환 시 max_iterations 이전에 루프 종료."""
    june = JuneAgent(max_iterations=3)

    # Mock 팀 에이전트 교체
    june._march.implement = MagicMock(return_value=make_result("march", AgentRole.DEVELOPER, "코드"))
    june._april.write_tests = MagicMock(return_value=make_result("april", AgentRole.TESTER, "테스트"))
    june._may.review = MagicMock(return_value=make_approved_result("may", AgentRole.REVIEWER))

    result = june.orchestrate("태스크")
    assert result["iterations"] == 1
    june._may.review.assert_called_once()


def test_june_orchestrate_loops_until_max(mock_anthropic_client):
    """CHANGES_REQUESTED 시 max_iterations까지 반복."""
    june = JuneAgent(max_iterations=2)

    june._march.implement = MagicMock(return_value=make_result("march", AgentRole.DEVELOPER, "코드"))
    june._march.refactor = MagicMock(return_value=make_result("march", AgentRole.DEVELOPER, "개선된 코드"))
    june._april.write_tests = MagicMock(return_value=make_result("april", AgentRole.TESTER, "테스트"))
    june._april.update_tests = MagicMock(return_value=make_result("april", AgentRole.TESTER, "업데이트 테스트"))
    june._may.review = MagicMock(
        return_value=AgentResult(agent_name="may", role=AgentRole.REVIEWER, content="CHANGES_REQUESTED", success=True)
    )

    result = june.orchestrate("태스크")
    assert result["iterations"] == 2
    assert june._may.review.call_count == 2
