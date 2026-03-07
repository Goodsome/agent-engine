from agent_engine.shared.models import ValueObject
from uuid import UUID


class JobId(ValueObject):
    """调度派发任务的唯一标识"""

    value: UUID
