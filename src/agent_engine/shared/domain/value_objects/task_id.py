from agent_engine.shared.models import ValueObject
from uuid import UUID


class TaskId(ValueObject):
    """关联到远端 TaskGraph 的任务标识"""

    value: UUID
