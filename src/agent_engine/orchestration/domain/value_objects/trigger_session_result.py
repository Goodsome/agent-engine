from agent_engine.shared.models import ValueObject
from agent_engine.shared.domain.value_objects.session_id import SessionId


class TriggerSessionResult(ValueObject):
    """触发 Agent 会话的结果"""

    session_id: SessionId
    output: str | None = None
    is_success: bool = True
