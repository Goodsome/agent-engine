from agent_engine.shared.models import ValueObject


class FeishuMessageId(ValueObject):
    """飞书消息唯一标识"""

    value: str

    @classmethod
    def create(cls, value: str) -> "FeishuMessageId":
        """创建飞书消息ID"""
        return cls(value=value)

    @classmethod
    def reconstitute(cls, value: str) -> "FeishuMessageId":
        """从原始值重建"""
        return cls(value=value)

    def __str__(self) -> str:
        return self.value

    def serialize(self) -> str:
        return self.value