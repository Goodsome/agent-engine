from agent_engine.shared.models import ValueObject
from uuid import UUID


class SessionId(ValueObject):
    """Agent 执行会话的唯一标识"""

    value: UUID
