from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(Enum):
    DEVELOPER = "march"
    TESTER = "april"
    REVIEWER = "may"
    ORCHESTRATOR = "june"


@dataclass
class Message:
    role: str   # "user" | "assistant"
    content: str


@dataclass
class AgentResult:
    agent_name: str
    role: AgentRole
    content: str
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamTask:
    description: str
    context: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
