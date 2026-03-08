import uuid
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.orchestration.domain.ports.sop_repository import SopRepository
from dataclasses import dataclass
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from pydantic import BaseModel


class StartInitialWorkflowCommand(BaseModel):
    raw_requirement: str


class StartInitialWorkflowResult(BaseModel):
    initial_session_id: str


@dataclass
class StartInitialWorkflow:
    """CLI 入口：接收用户自然语言指令，加载 sop_story_decompose，拉起一个 Agent Session 进行需求拆解。"""

    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort
    sop_repo: SopRepository
    project_id: str

    async def execute(
        self, cmd: StartInitialWorkflowCommand
    ) -> StartInitialWorkflowResult:
        job = DispatchJob(
            id=JobId(value=uuid.uuid4()),
            status=JobStatus.PENDING
        )
        await self.job_repo.save(job=job)

        system_prompt = await self.sop_repo.get_sop(
            planning_level="story", status="ready"
        )

        session_id = await self.execution_trigger.trigger_session(
            job_id=job.id,
            system_prompt=system_prompt,
            requirement=cmd.raw_requirement,
            context_payload={"project_id": self.project_id},
        )

        job.mark_running(session_id=session_id)
        await self.job_repo.save(job=job)

        return StartInitialWorkflowResult(initial_session_id=str(session_id.value))
