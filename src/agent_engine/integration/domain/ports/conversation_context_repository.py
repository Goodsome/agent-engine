from abc import ABC, abstractmethod
from agent_engine.integration.domain.aggregates.conversation_context import (
    ConversationContext,
)
from agent_engine.integration.domain.value_objects.chat_id import ChatId


class ConversationContextRepository(ABC):
    """会话上下文仓储 - 持久化聊天对话历史"""

    @abstractmethod
    async def save(self, context: ConversationContext) -> None:
        """保存会话上下文

        Args:
            context: 要保存的会话上下文
        """
        ...

    @abstractmethod
    async def find_by_chat_id(self, chat_id: ChatId) -> ConversationContext | None:
        """根据会话ID查找上下文

        Args:
            chat_id: 飞书会话ID

        Returns:
            会话上下文，如果不存在则返回 None
        """
        ...

    @abstractmethod
    async def delete(self, chat_id: ChatId) -> None:
        """删除会话上下文

        Args:
            chat_id: 飞书会话ID
        """
        ...