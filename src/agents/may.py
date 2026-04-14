from agents.base import BaseAgent
from agents.models import AgentRole, AgentResult


class MayAgent(BaseAgent):
    """코드 리뷰 전문 에이전트. 품질, 보안, 성능 검토에 특화."""

    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="may",
            role=AgentRole.REVIEWER,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """당신은 May, 시니어 코드 리뷰어 에이전트입니다.

역할:
- 코드 품질, 보안 취약점, 성능 문제를 검토합니다
- Python 모범 사례 및 SOLID 원칙 준수 여부를 평가합니다
- 구체적이고 실행 가능한 개선 제안을 제공합니다
- 테스트 커버리지와 코드 설계의 테스트 가능성을 평가합니다

출력 형식 (구조화):
1. 종합 평가 (APPROVED / CHANGES_REQUESTED / REJECTED)
2. 심각도별 이슈 목록 (CRITICAL / MAJOR / MINOR)
3. 구체적인 개선 제안 (코드 예시 포함)
4. 긍정적인 부분 언급

중립적이고 건설적인 피드백을 제공합니다."""

    def review(
        self,
        code: str,
        tests: str = "",
        requirements: str = "",
    ) -> AgentResult:
        """코드와 테스트를 종합적으로 리뷰."""
        prompt = f"다음 코드를 리뷰해주세요.\n\n구현 코드:\n```python\n{code}\n```"
        if tests:
            prompt += f"\n\n테스트 코드:\n```python\n{tests}\n```"
        if requirements:
            prompt += f"\n\n요구사항:\n{requirements}"
        return self.run(prompt)
