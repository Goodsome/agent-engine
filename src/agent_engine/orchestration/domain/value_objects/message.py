from agent_engine.shared.domain.core.value_object import ValueObject
from agent_engine.orchestration.domain.enums import MessageRole


class Message(ValueObject):

    role: MessageRole
    content: str
    