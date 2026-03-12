from agent_engine.shared.models import ValueObject
from typing import Any


class ChatId(ValueObject):
    """飞书会话唯一标识"""

    value: str

    @classmethod
    def create(cls, value: str) -> "ChatId":
        """创建会话ID"""
        return cls(value=value)

    @classmethod
    def reconstitute(cls, value: str) -> "ChatId":
        """从原始值重建"""
        return cls(value=value)

    def __str__(self) -> str:
        return self.value

    def serialize(self) -> str:
        return self.value