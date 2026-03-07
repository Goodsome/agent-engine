from agent_engine.execution.domain.aggregates.agent_session import AgentSession
from agent_engine.execution.domain.ports.agent_session_repository import (
    AgentSessionRepository,
)
from dataclasses import dataclass, field

from agent_engine.shared.domain.value_objects.session_id import SessionId


@dataclass
class SqlAlchemySessionRepository(AgentSessionRepository):
    """使用 PostgreSQL/SQLite 持久化 Agent 会话日志和状态"""
    
    _storage: dict[str, AgentSession] = field(default_factory=dict)

    def save(self, session: AgentSession) -> None:
        self._storage[str(session.id.value)] = session

    def delete(self, agent_session_id: SessionId) -> None:
        if str(agent_session_id.value) in self._storage:
            del self._storage[str(agent_session_id.value)]

    def find_by_id(self, agent_session_id: SessionId) -> AgentSession | None:
        return self._storage.get(str(agent_session_id.value))
