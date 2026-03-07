from abc import ABC, abstractmethod
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from uuid import UUID

from src.agent_engine.shared.domain.value_objects.job_id import JobId


class DispatchJobRepository(ABC):

    @abstractmethod
    async def save(self, job: DispatchJob) -> None: ...

    @abstractmethod
    async def delete(self, dispatch_job_id: JobId) -> None: ...

    @abstractmethod
    async def find_by_id(self, dispatch_job_id: JobId) -> DispatchJob | None: ...
