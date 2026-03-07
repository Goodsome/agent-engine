from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from dataclasses import dataclass
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from pydantic import BaseModel


class StartInitialWorkflowCommand(BaseModel):
    raw_requirement: str


class StartInitialWorkflowResult(BaseModel):
    initial_session_id: str


import uuid
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.shared.domain.value_objects.job_id import JobId

@dataclass
class StartInitialWorkflow:
    """CLI 入口：接收用户自然语言指令，直接拉起一个 Planner Session，让 Agent 负责向 TaskGraph 写入初始节点。"""

    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort

    def execute(
        self, cmd: StartInitialWorkflowCommand
    ) -> StartInitialWorkflowResult:
        job = DispatchJob(
            id=JobId(value=uuid.uuid4()),
            status=JobStatus.PENDING
        )
        self.job_repo.save(job=job)

        session_id = self.execution_trigger.trigger_session(
            job_id=job.id,
            requirement=cmd.raw_requirement
        )

        job.mark_running(session_id=session_id)
        self.job_repo.save(job=job)

        return StartInitialWorkflowResult(initial_session_id=str(session_id.value))
