from agent_engine.shared.domain.value_objects.job_id import JobId
from dataclasses import dataclass
from typing import Any
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
    TriggerSessionResult,
)
from agent_engine.shared.domain.enums import ModelTier
from agent_engine.orchestration.application.use_cases.execute_agent_session import (
    ExecuteAgentSession,
    ExecuteAgentSessionCommand,
)


@dataclass
class InProcessExecutionTrigger(ExecutionTriggerPort):
    """进程内直接调用 Execution 域的应用层服务 (UseCase) 触发任务"""

    execute_agent_session: ExecuteAgentSession

    async def trigger_session(
        self,
        job_id: JobId,
        system_prompt: str,
        requirement: str | None = None,
        context_payload: dict[str, Any] | None = None,
        model_tier: ModelTier | None = None,
    ) -> TriggerSessionResult:
        cmd = ExecuteAgentSessionCommand(
            job_id=job_id,
            system_prompt=system_prompt,
            requirement=requirement,
            context_payload=context_payload or {},
            model_tier=model_tier,
        )
        result = await self.execute_agent_session.execute(cmd)
        return TriggerSessionResult(
            session_id=result.session_id,
            output=result.output,
            is_success=result.is_success,
        )
