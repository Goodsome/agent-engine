import uuid
from dataclasses import dataclass
from pydantic import BaseModel

from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.orchestration.domain.ports.sop_repository import SopRepository
from agent_engine.shared.domain.value_objects.job_id import JobId


class HandleTaskReadyEventResult(BaseModel):
    job_id: str
    session_id: str


@dataclass
class HandleTaskReadyEvent:
    """处理 TaskReadyEvent 事件的用例：创建 DispatchJob -> 加载 SOP -> 触发执行"""

    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort
    sop_repo: SopRepository

    async def execute(self, event: TaskReadyEvent) -> HandleTaskReadyEventResult:
        job = DispatchJob(
            id=JobId(value=uuid.uuid4()),
            task_id=event.task_id,
            status=JobStatus.PENDING,
        )
        await self.job_repo.save(job=job)

        system_prompt = await self.sop_repo.get_sop(
            planning_level=event.planning_level,
            status=event.status,
        )

        session_id = await self.execution_trigger.trigger_session(
            job_id=job.id,
            system_prompt=system_prompt,
            requirement=f"执行任务: {event.task_id.value}",
            context_payload={"task_id": str(event.task_id.value)},
        )

        job.mark_running(session_id=session_id)
        await self.job_repo.save(job=job)

        return HandleTaskReadyEventResult(
            job_id=str(job.id.value),
            session_id=str(session_id.value),
        )
