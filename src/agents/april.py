from agents.base import BaseAgent
from agents.models import AgentRole, AgentResult


class AprilAgent(BaseAgent):
    """테스트 개발 전문 에이전트. pytest 기반 테스트 작성에 특화."""

    def __init__(self, **kwargs) -> None:
        super().__init__(
            name="april",
            role=AgentRole.TESTER,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """당신은 April, 테스트 자동화 전문 에이전트입니다.

역할:
- pytest를 사용한 포괄적인 테스트 스위트를 작성합니다
- 단위 테스트, 통합 테스트, 엣지 케이스를 모두 커버합니다
- pytest-mock을 활용한 의존성 모킹을 구현합니다
- 테스트 픽스처와 파라미터화를 적극 활용합니다

출력 형식:
- tests/ 경로의 완전한 테스트 파일을 제공합니다
- 각 테스트의 목적을 docstring으로 설명합니다
- 테스트 커버리지 전략을 설명합니다

절대로 구현 코드를 작성하지 않습니다. 테스트 코드에만 집중합니다."""

    def write_tests(self, code: str, requirements: str = "") -> AgentResult:
        """구현 코드에 대한 테스트를 작성."""
        prompt = (
            f"다음 코드에 대한 포괄적인 pytest 테스트를 작성해주세요.\n\n"
            f"구현 코드:\n```python\n{code}\n```\n"
        )
        if requirements:
            prompt += f"\n요구사항:\n{requirements}"
        return self.run(prompt)

    def update_tests(self, tests: str, code_changes: str) -> AgentResult:
        """코드 변경에 따른 테스트 업데이트."""
        prompt = (
            f"코드 변경사항에 맞게 테스트를 업데이트해주세요.\n\n"
            f"기존 테스트:\n```python\n{tests}\n```\n\n"
            f"코드 변경사항:\n{code_changes}"
        )
        return self.run(prompt)
