from dataclasses import dataclass
from typing import Any, cast
from typing_extensions import override
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agent_engine.orchestration.domain.aggregates.agent_session import AgentSession
from agent_engine.orchestration.domain.ports.agent_session_repository import (
    AgentSessionRepository,
)
from agent_engine.orchestration.domain.enums import SessionStatus
from agent_engine.orchestration.domain.value_objects.message import Message
from agent_engine.orchestration.infrastructure.orm_models.agent_session_model import (
    AgentSessionModel,
)
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.project_id import ProjectId


@dataclass
class SqlAlchemySessionRepository(AgentSessionRepository):
    """使用 PostgreSQL 持久化 Agent 会话日志和状态"""

    session_factory: async_sessionmaker[AsyncSession]

    @override
    async def save(self, session: AgentSession) -> None:
        async with self.session_factory() as db_session:
            # 尝试查找现有记录（upsert 逻辑）
            model = await db_session.get(AgentSessionModel, session.id.value)

            if model is None:
                model = AgentSessionModel(
                    id=session.id.value,
                    task_id=session.task_id.value,
                    project_id=session.project_id.value,
                    status=session.status.value,
                    context_payload=session.context_payload,
                    system_prompt=session.system_prompt,
                    messages=[m.model_dump() for m in session.messages],
                )
                db_session.add(model)
            else:
                model.status = session.status.value
                model.context_payload = cast(dict[str, Any], session.context_payload)
                model.system_prompt = session.system_prompt
                model.messages = [m.model_dump() for m in session.messages]
                # task_id 和 project_id 通常不更改

            await db_session.commit()

    @override
    async def delete(self, agent_session_id: SessionId) -> None:
        async with self.session_factory() as db_session:
            _ = await db_session.execute(
                delete(AgentSessionModel).where(
                    AgentSessionModel.id == agent_session_id.value
                )
            )
            await db_session.commit()

    @override
    async def find_by_id(self, agent_session_id: SessionId) -> AgentSession | None:
        async with self.session_factory() as db_session:
            model = await db_session.get(AgentSessionModel, agent_session_id.value)
            if model:
                return self._map_to_domain(model)
            return None

    @override
    async def find_by_task_id(self, task_id: TaskId) -> AgentSession | None:
        async with self.session_factory() as db_session:
            result = await db_session.execute(
                select(AgentSessionModel).where(
                    AgentSessionModel.task_id == task_id.value
                )
            )
            model = result.scalar_one_or_none()
            if model:
                return self._map_to_domain(model)
            return None

    def _map_to_domain(self, model: AgentSessionModel) -> AgentSession:
        return AgentSession(
            id=SessionId(value=model.id),
            task_id=TaskId(value=model.task_id),
            project_id=ProjectId(value=model.project_id),
            status=SessionStatus(model.status),
            context_payload=model.context_payload,
            system_prompt=model.system_prompt,
            messages=[Message(**m) for m in model.messages],
        )
