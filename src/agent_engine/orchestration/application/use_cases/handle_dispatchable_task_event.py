import uuid
from dataclasses import dataclass
from typing import Union
from pydantic import BaseModel

from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
from agent_engine.orchestration.domain.events.task_review_requested_event import TaskReviewRequestedEvent
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.orchestration.domain.ports.sop_repository import SopRepository
from agent_engine.shared.domain.value_objects.job_id import JobId

class HandleDispatchableTaskEventCommand(BaseModel):
    event: TaskReadyEvent | TaskReviewRequestedEvent

class HandleDispatchableTaskEventResult(BaseModel):
    job_id: str
    session_id: str


@dataclass
class HandleDispatchableTaskEvent:
    """处理可调度任务事件（TaskReadyEvent, TaskReviewRequestedEvent）的用例：创建 DispatchJob -> 加载 SOP -> 触发执行"""

    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort
    sop_repo: SopRepository

    async def execute(self, cmd: HandleDispatchableTaskEventCommand) -> HandleDispatchableTaskEventResult:
        event = cmd.event
        job = DispatchJob(
            id=JobId(value=uuid.uuid4()),
            task_id=event.task_id,
            status=JobStatus.PENDING,
        )
        await self.job_repo.save(job=job)

        sop_content = await self.sop_repo.get_sop(
            planning_level=event.planning_level,
            status=event.status,
        )

        result = await self.execution_trigger.trigger_session(
            job_id=job.id,
            system_prompt=sop_content.system_prompt,
            model_tier=sop_content.model_tier,
            requirement=f"执行任务(状态:{event.status.value}): {event.task_id.value}",
            context_payload={"task_id": str(event.task_id.value), "status": event.status.value},
        )

        job.mark_running(session_id=result.session_id)
        await self.job_repo.save(job=job)

        return HandleDispatchableTaskEventResult(
            job_id=str(job.id.value),
            session_id=str(result.session_id.value),
        )
