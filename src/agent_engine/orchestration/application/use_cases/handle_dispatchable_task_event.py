import uuid
from dataclasses import dataclass
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
from agent_engine.agent_registry.domain.ports.blueprint_registry import BlueprintRegistryPort
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
    blueprint_registry: BlueprintRegistryPort

    async def execute(self, cmd: HandleDispatchableTaskEventCommand) -> HandleDispatchableTaskEventResult:
        event = cmd.event
        job = DispatchJob(
            id=JobId(value=uuid.uuid4()),
            task_id=event.task_id,
            status=JobStatus.PENDING,
        )
        await self.job_repo.save(job=job)

        blueprint = await self.blueprint_registry.get_blueprint(
            scope_level=event.scope_level.value,
            architecture_layer=event.architecture_layer.value if event.architecture_layer else None,
        )
        # Determine requirement based on event type
        from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
        if isinstance(event, TaskReadyEvent):
            requirement = f"执行任务: {event.task_id.value}"
        else:  # TaskReviewRequestedEvent
            requirement = f"审查任务: {event.task_id.value}"
        context_payload = {
            "task_id": str(event.task_id.value),
            "bounded_context": event.bounded_context,
        }

        result = await self.execution_trigger.trigger_session(
            job_id=job.id,
            system_prompt=blueprint.system_prompt,
            model_tier=blueprint.model_tier,
            requirement=requirement,
            context_payload=context_payload,
        )

        job.mark_running(session_id=result.session_id)
        await self.job_repo.save(job=job)

        return HandleDispatchableTaskEventResult(
            job_id=str(job.id.value),
            session_id=str(result.session_id.value),
        )
