from abc import ABC, abstractmethod
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.execution.domain.enums import ModelTier
from agent_engine.orchestration.domain.value_objects.trigger_session_result import TriggerSessionResult


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
