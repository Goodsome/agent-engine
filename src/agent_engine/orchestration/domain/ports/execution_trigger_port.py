from abc import ABC, abstractmethod
from dataclasses import dataclass
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.execution.domain.enums import ModelTier


@dataclass(frozen=True)
class TriggerSessionResult:
    """触发 Agent 会话的结果"""

    session_id: SessionId
    output: str | None = None
    is_success: bool = True


class ExecutionTriggerPort(ABC):
    """定义一个明确的跨上下文调用端口，用于触发 Execution 域。"""

    @abstractmethod
    async def trigger_session(
        self,
        job_id: JobId,
        system_prompt: str,
        requirement: str | None = None,
        context_payload: dict | None = None,
        model_tier: ModelTier | None = None,
    ) -> TriggerSessionResult: ...
