from agent_engine.shared.models import Aggregate
from pydantic import Field
from agent_engine.integration.domain.value_objects.chat_id import ChatId
from agent_engine.shared.domain.value_objects.session_id import SessionId


class ConversationContext(Aggregate):
    """聚合根 - 飞书会话的对话上下文，用于多轮对话记忆"""

    chat_id: ChatId
    messages: list[dict] = Field(default_factory=list)
    current_session_id: SessionId | None = Field(default=None)

    def add_message(self, role: str, content: str) -> None:
        """添加消息到对话历史

        Args:
            role: 消息角色 (user/assistant)
            content: 消息内容
        """
        self.messages.append({"role": role, "content": content})

    def set_session(self, session_id: SessionId) -> None:
        """设置当前会话ID

        Args:
            session_id: Agent 会话ID
        """
        self.current_session_id = session_id

    def clear_messages(self) -> None:
        """清空对话历史"""
        self.messages = []

    @classmethod
    def create(cls, chat_id: ChatId) -> "ConversationContext":
        """创建新的对话上下文

        Args:
            chat_id: 飞书会话ID

        Returns:
            新的 ConversationContext 实例
        """
        return cls(chat_id=chat_id, messages=[])