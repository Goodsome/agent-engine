from typing import Optional
from agent_engine.shared.domain.core.value_object import ValueObject
from agent_engine.integration.domain.value_objects.chat_id import ChatId
from agent_engine.integration.domain.enums import ChatType
from agent_engine.integration.domain.value_objects.feishu_message_id import (
    FeishuMessageId,
)


class FeishuMessagePayload(ValueObject):
    """飞书消息负载 - 防腐层数据契约"""

    message_id: FeishuMessageId
    chat_id: ChatId
    chat_type: ChatType
    content: str
    sender_id: Optional[str] = None  # 某些情况下可能为空
