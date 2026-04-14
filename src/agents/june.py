import os

from agents.base import BaseAgent
from agents.march import MarchAgent
from agents.april import AprilAgent
from agents.may import MayAgent
from agents.models import AgentRole, AgentResult


class _TaskState:
    """오케스트레이션 중 상태 추적용 내부 클래스."""

    def __init__(self, description: str) -> None:
        self.description = description
        self.spec: str = ""
        self.code: str = ""
        self.tests: str = ""
        self.review_feedback: str = ""


class JuneAgent(BaseAgent):
    """팀 총괄 오케스트레이터 에이전트."""

    def __init__(
        self,
        max_iterations: int | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            name="june",
            role=AgentRole.ORCHESTRATOR,
            **kwargs,
        )
        self.max_iterations = max_iterations or int(
            os.getenv("MAX_ITERATIONS", "3")
        )
        self._march = MarchAgent(model=self.model)
        self._april = AprilAgent(model=self.model)
        self._may = MayAgent(model=self.model)

    @property
    def system_prompt(self) -> str:
        return """당신은 June, AI 개발팀 총괄 오케스트레이터입니다.

팀 구성:
- March: Python 개발 전문가 (구현 담당)
- April: 테스트 자동화 전문가 (테스트 담당)
- May: 시니어 코드 리뷰어 (품질 담당)

역할:
- 사용자 요청을 분석하여 명확한 작업 명세를 작성합니다
- 팀 결과물을 종합하여 최종 보고서를 생성합니다
- 반복 개선 여부와 방향을 결정합니다

출력 형식: 간결하고 구조화된 계획 또는 보고서."""

    def orchestrate(self, user_request: str) -> dict:
        """멀티 에이전트 파이프라인 실행.

        Returns:
            {
                "success": bool,
                "iterations": int,
                "artifacts": {"code": str, "tests": str, "review": str},
                "summary": str,
                "history": list[dict],
            }
        """
        history: list[dict] = []
        task = _TaskState(description=user_request)

        # 1단계: June이 작업 분석 및 명세 작성
        plan_result = self.run(
            f"다음 요청을 분석하고 개발 명세를 작성해주세요:\n\n{user_request}"
        )
        task.spec = plan_result.content
        history.append({"step": "planning", "agent": "june", "result": plan_result})

        # 2단계: March가 구현
        march_result = self._march.implement(task.spec)
        task.code = march_result.content
        history.append(
            {"step": "implementation", "agent": "march", "result": march_result}
        )

        may_result: AgentResult | None = None
        iteration = 0
        for iteration in range(self.max_iterations):
            # 3단계: April이 테스트 작성/업데이트
            if iteration == 0:
                april_result = self._april.write_tests(task.code, task.spec)
            else:
                april_result = self._april.update_tests(task.tests, task.review_feedback)
            task.tests = april_result.content
            history.append(
                {
                    "step": f"testing_iter{iteration}",
                    "agent": "april",
                    "result": april_result,
                }
            )

            # 4단계: May가 리뷰
            may_result = self._may.review(task.code, task.tests, task.spec)
            task.review_feedback = may_result.content
            history.append(
                {
                    "step": f"review_iter{iteration}",
                    "agent": "may",
                    "result": may_result,
                }
            )

            # 승인 여부 판단
            if "APPROVED" in may_result.content.upper():
                break

            # 5단계: March가 피드백 반영 (마지막 반복이 아닐 때)
            if iteration < self.max_iterations - 1:
                march_result = self._march.refactor(task.code, task.review_feedback)
                task.code = march_result.content
                history.append(
                    {
                        "step": f"refactor_iter{iteration}",
                        "agent": "march",
                        "result": march_result,
                    }
                )

        # 6단계: June이 최종 보고서 생성
        summary_result = self.run(
            f"팀 작업 결과를 요약해주세요:\n"
            f"- 총 반복 횟수: {iteration + 1}\n"
            f"- 리뷰 결과: {task.review_feedback[:200]}..."
        )

        return {
            "success": may_result.success if may_result else False,
            "iterations": iteration + 1,
            "artifacts": {
                "code": task.code,
                "tests": task.tests,
                "review": task.review_feedback,
            },
            "summary": summary_result.content,
            "history": history,
        }

    @property
    def team(self) -> dict[str, BaseAgent]:
        return {
            "march": self._march,
            "april": self._april,
            "may": self._may,
        }
