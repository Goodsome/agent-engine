from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from dataclasses import dataclass, field

from agent_engine.shared.domain.value_objects.job_id import JobId


@dataclass
class SqlAlchemyDispatchJobRepository(DispatchJobRepository):
    """使用 PostgreSQL/SQLite 持久化 Job 记录"""
    
    _storage: dict[str, DispatchJob] = field(default_factory=dict)

    def save(self, job: DispatchJob) -> None:
        self._storage[str(job.id.value)] = job

    def delete(self, dispatch_job_id: JobId) -> None:
        if str(dispatch_job_id.value) in self._storage:
            del self._storage[str(dispatch_job_id.value)]

    def find_by_id(self, dispatch_job_id: JobId) -> DispatchJob | None:
        return self._storage.get(str(dispatch_job_id.value))
