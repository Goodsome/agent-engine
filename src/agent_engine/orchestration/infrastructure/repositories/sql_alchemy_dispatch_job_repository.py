from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from agent_engine.shared.domain.value_objects.job_id import JobId


@dataclass
class SqlAlchemyDispatchJobRepository(DispatchJobRepository):
    """使用 PostgreSQL 持久化 Job 记录"""
    
    session_factory: async_sessionmaker[AsyncSession]

    async def save(self, job: DispatchJob) -> None:
        async with self.session_factory():
            # TODO: 映射 Domain Object -> SQLAlchemy Model
            # db_session.add(model)
            # await db_session.commit()
            pass

    async def delete(self, dispatch_job_id: JobId) -> None:
        async with self.session_factory():
            pass

    async def find_by_id(self, dispatch_job_id: JobId) -> DispatchJob | None:
        async with self.session_factory():
            return None
