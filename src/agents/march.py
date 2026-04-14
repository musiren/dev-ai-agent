from agents.base import BaseAgent
from agents.models import AgentRole, AgentResult


class MarchAgent(BaseAgent):
    """개발 전문 에이전트. 코드 구현에 특화."""

    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="march",
            role=AgentRole.DEVELOPER,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """당신은 March, 숙련된 Python 개발자 에이전트입니다.

역할:
- 명확하고 유지보수 가능한 Python 코드를 작성합니다
- PEP 8, type hints, docstring을 준수합니다
- 주어진 요구사항을 코드로 구현합니다
- 코드에 포함된 엣지 케이스를 처리합니다

출력 형식:
- 구현 코드를 완전한 Python 모듈 형태로 제공합니다
- 핵심 설계 결정사항에 간략한 설명을 덧붙입니다
- 파일 경로를 명시합니다

절대로 테스트 코드를 작성하지 않습니다. 구현 코드에만 집중합니다."""

    def implement(self, requirements: str) -> AgentResult:
        """요구사항을 코드로 구현."""
        prompt = f"다음 요구사항을 Python 코드로 구현해주세요:\n\n{requirements}"
        return self.run(prompt)

    def refactor(self, code: str, feedback: str) -> AgentResult:
        """리뷰 피드백을 반영하여 코드 개선."""
        prompt = (
            f"다음 코드를 리뷰 피드백에 따라 개선해주세요.\n\n"
            f"현재 코드:\n```python\n{code}\n```\n\n"
            f"피드백:\n{feedback}"
        )
        return self.run(prompt)
