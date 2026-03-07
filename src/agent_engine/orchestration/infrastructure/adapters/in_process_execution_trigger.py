from typing import Union
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from dataclasses import dataclass
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)


@dataclass
class InProcessExecutionTrigger(ExecutionTriggerPort):
    """进程内直接调用 Execution 域的应用层服务 (UseCase) 触发任务"""

    def trigger_session(
        self,
        job_id: JobId,
        task_id: TaskId | None = None,
        requirement: str | None = None,
    ) -> SessionId: ...
