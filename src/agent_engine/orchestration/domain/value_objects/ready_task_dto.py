from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.models import ValueObject
from typing import Union
from pydantic import Field


class ReadyTaskDTO(ValueObject):
    """防腐层数据契约：从 TaskGraph 读取的、随时可被派发的任务快照"""

    task_id: TaskId
    planning_level: str
    name: str
    intent: str | None = Field(default=None)
