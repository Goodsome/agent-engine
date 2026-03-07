from typing import Union
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from dataclasses import dataclass
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.execution.application.use_cases.execute_agent_session import ExecuteAgentSession, ExecuteAgentSessionCommand
from agent_engine.execution.domain.enums import SessionType

@dataclass
class InProcessExecutionTrigger(ExecutionTriggerPort):
    """进程内直接调用 Execution 域的应用层服务 (UseCase) 触发任务"""
    
    execute_agent_session: ExecuteAgentSession

    def trigger_session(
        self,
        job_id: JobId,
        task_id: TaskId | None = None,
        requirement: str | None = None,
    ) -> SessionId:
        cmd = ExecuteAgentSessionCommand(
            job_id=job_id,
            task_id=task_id,
            requirement=requirement,
            session_type=SessionType.PLANNER # Assuming planner type as default entry
        )
        result = self.execute_agent_session.execute(cmd)
        return result.session_id
