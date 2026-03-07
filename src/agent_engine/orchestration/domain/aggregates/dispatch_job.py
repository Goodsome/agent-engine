from agent_engine.shared.models import Aggregate
from typing import Union
from pydantic import Field
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.shared.domain.value_objects.job_id import JobId


class DispatchJob(Aggregate):
    """聚合根 — 记录一次从 TaskGraph 拉取任务并尝试执行的分发记录。"""

    id: JobId
    task_id: TaskId | None = Field(default=None)
    status: JobStatus
    session_id: SessionId | None = Field(default=None)

    def mark_running(self, session_id: SessionId) -> None: ...

    def mark_completed(self) -> None: ...

    def mark_failed(self, reason: str) -> None: ...
