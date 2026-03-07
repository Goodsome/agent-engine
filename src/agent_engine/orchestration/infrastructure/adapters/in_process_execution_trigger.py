from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from dataclasses import dataclass
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.execution.application.use_cases.execute_agent_session import (
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
        context_payload: dict | None = None,
    ) -> SessionId:
        cmd = ExecuteAgentSessionCommand(
            job_id=job_id,
            system_prompt=system_prompt,
            requirement=requirement,
            context_payload=context_payload or {},
        )
        result = await self.execute_agent_session.execute(cmd)
        return result.session_id
