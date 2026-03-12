from abc import ABC, abstractmethod
from typing import Callable, Awaitable
from agent_engine.integration.domain.value_objects.chat_id import ChatId
from agent_engine.integration.domain.value_objects.feishu_message_id import (
    FeishuMessageId,
)
from agent_engine.integration.domain.value_objects.feishu_message_payload import (
    FeishuMessagePayload,
)


class FeishuClientPort(ABC):
    """飞书客户端端口 - 处理WebSocket连接和API调用"""

    @abstractmethod
    async def send_message(self, chat_id: ChatId, content: str) -> FeishuMessageId:
        """发送新消息到会话

        Args:
            chat_id: 会话ID
            content: 消息内容

        Returns:
            发送的消息ID
        """
        ...

    @abstractmethod
    async def reply_message(
        self, message_id: FeishuMessageId, content: str
    ) -> FeishuMessageId:
        """回复消息

        Args:
            message_id: 要回复的消息ID
            content: 回复内容

        Returns:
            回复的消息ID
        """
        ...

    @abstractmethod
    async def update_message(self, message_id: FeishuMessageId, content: str) -> None:
        """更新消息内容（用于流式输出）

        Args:
            message_id: 要更新的消息ID
            content: 新的消息内容
        """
        ...

    @abstractmethod
    def set_message_handler(
        self, handler: Callable[[FeishuMessagePayload], Awaitable[None]]
    ) -> None:
        """设置消息处理器

        Args:
            handler: 异步消息处理函数
        """
        ...

    @abstractmethod
    async def start_listener(self) -> None:
        """启动 WebSocket 监听器"""
        ...