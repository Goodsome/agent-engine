from agent_engine.execution.domain.aggregates.agent_session import AgentSession
from agent_engine.execution.domain.ports.agent_session_repository import (
    AgentSessionRepository,
)
from uuid import UUID
from dataclasses import dataclass

from src.agent_engine.shared.domain.value_objects.session_id import SessionId


@dataclass
class SqlAlchemySessionRepository(AgentSessionRepository):
    """使用 PostgreSQL/SQLite 持久化 Agent 会话日志和状态"""

    def save(self, session: AgentSession) -> None: ...

    def delete(self, agent_session_id: SessionId) -> None: ...

    def find_by_id(self, agent_session_id: SessionId) -> AgentSession | None: ...
