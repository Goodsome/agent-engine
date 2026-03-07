from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from uuid import UUID
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from dataclasses import dataclass

from src.agent_engine.shared.domain.value_objects.job_id import JobId


@dataclass
class SqlAlchemyDispatchJobRepository(DispatchJobRepository):
    """使用 PostgreSQL/SQLite 持久化 Job 记录"""

    def save(self, job: DispatchJob) -> None: ...

    def delete(self, dispatch_job_id: JobId) -> None: ...

    def find_by_id(self, dispatch_job_id: JobId) -> DispatchJob | None: ...
