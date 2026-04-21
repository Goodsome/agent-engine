from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agent_engine.orchestration.domain.aggregates.agent_session import AgentSession
from agent_engine.orchestration.domain.ports.agent_session_repository import (
    AgentSessionRepository,
)
from agent_engine.shared.domain.value_objects.session_id import SessionId


@dataclass
class SqlAlchemySessionRepository(AgentSessionRepository):
    """使用 PostgreSQL 持久化 Agent 会话日志和状态"""
    
    session_factory: async_sessionmaker[AsyncSession]

    async def save(self, session: AgentSession) -> None:
        async with self.session_factory():
            # TODO: 映射 Domain Object -> SQLAlchemy Model
            # db_session.add(model)
            # await db_session.commit()
            pass

    async def delete(self, agent_session_id: SessionId) -> None:
        async with self.session_factory():
            pass

    async def find_by_id(self, agent_session_id: SessionId) -> AgentSession | None:
        async with self.session_factory():
            return None
