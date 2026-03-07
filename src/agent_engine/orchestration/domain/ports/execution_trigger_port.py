from abc import ABC, abstractmethod
from typing import Union
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.session_id import SessionId


class ExecutionTriggerPort(ABC):
    """定义一个明确的跨上下文调用端口，用于触发 Execution 域。"""

    @abstractmethod
    def trigger_session(
        self,
        job_id: JobId,
        task_id: TaskId | None = None,
        requirement: str | None = None,
    ) -> SessionId: ...
