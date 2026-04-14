import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import anthropic

from agents.models import AgentRole, AgentResult, Message

load_dotenv()

class BaseAgent(ABC):
    """모든 에이전트의 공통 기반 클래스."""

    def __init__(
        self,
        name: str,
        role: AgentRole,
        model: str | None = None,
        enable_thinking: bool = True,
    ) -> None:
        self.name = name
        self.role = role
        self.model = model or os.getenv("DEFAULT_MODEL", "claude-opus-4-6")
        self.enable_thinking = enable_thinking
        self._client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self._history: list[Message] = []

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """각 에이전트의 역할별 시스템 프롬프트."""
        ...

    def _build_api_messages(self) -> list[dict]:
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self._history
        ]

    def _call_api(self, user_message: str) -> str:
        """Anthropic API 호출 (스트리밍, adaptive thinking 적용)."""
        self._history.append(Message(role="user", content=user_message))

        kwargs: dict = {
            "model": self.model,
            "max_tokens": 64000,
            "system": self.system_prompt,
            "messages": self._build_api_messages(),
        }
        if self.enable_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        full_text = ""
        with self._client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                full_text += text
            final = stream.get_final_message()

        # 텍스트 블록만 추출 (thinking 블록 제외)
        response_text = next(
            (b.text for b in final.content if b.type == "text"), full_text
        )

        self._history.append(Message(role="assistant", content=response_text))
        return response_text

    def run(self, task: str) -> AgentResult:
        """에이전트 실행 진입점."""
        try:
            content = self._call_api(task)
            return AgentResult(
                agent_name=self.name,
                role=self.role,
                content=content,
                success=True,
            )
        except anthropic.APIError as e:
            return AgentResult(
                agent_name=self.name,
                role=self.role,
                content=str(e),
                success=False,
                metadata={"error_type": type(e).__name__},
            )

    def reset_history(self) -> None:
        """대화 히스토리 초기화."""
        self._history = []

    @property
    def history(self) -> list[Message]:
        return list(self._history)
