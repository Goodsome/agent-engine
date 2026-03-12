from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agent_engine.integration.domain.aggregates.conversation_context import (
    ConversationContext,
)
from agent_engine.integration.domain.ports.conversation_context_repository import (
    ConversationContextRepository,
)
from agent_engine.integration.domain.value_objects.chat_id import ChatId


@dataclass
class SqlAlchemyConversationContextRepository(ConversationContextRepository):
    """使用 PostgreSQL 持久化会话上下文

    TODO: 实现数据库模型映射
    当前为内存实现，用于快速原型验证
    """

    session_factory: async_sessionmaker[AsyncSession]
    _cache: dict[str, ConversationContext] = None  # 临时内存缓存

    def __post_init__(self):
        if self._cache is None:
            self._cache = {}

    async def save(self, context: ConversationContext) -> None:
        """保存会话上下文

        Args:
            context: 要保存的会话上下文
        """
        # 临时使用内存存储
        # TODO: 实现数据库持久化
        chat_id_str = str(context.chat_id)
        self._cache[chat_id_str] = context

    async def find_by_chat_id(self, chat_id: ChatId) -> ConversationContext | None:
        """根据会话ID查找上下文

        Args:
            chat_id: 飞书会话ID

        Returns:
            会话上下文，如果不存在则返回 None
        """
        # 临时使用内存存储
        # TODO: 实现数据库查询
        chat_id_str = str(chat_id)
        return self._cache.get(chat_id_str)

    async def delete(self, chat_id: ChatId) -> None:
        """删除会话上下文

        Args:
            chat_id: 飞书会话ID
        """
        chat_id_str = str(chat_id)
        self._cache.pop(chat_id_str, None)