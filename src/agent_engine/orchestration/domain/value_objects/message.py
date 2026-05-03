from agent_engine.shared.models import ValueObject
from agent_engine.orchestration.domain.enums import MessageRole


class Message(ValueObject):

    role: MessageRole
    content: str
    