import uuid
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from dataclasses import dataclass
from pydantic import BaseModel
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from agent_engine.agent_registry.domain.ports.blueprint_registry import BlueprintRegistryPort

class StartInitialWorkflowCommand(BaseModel):
    raw_requirement: str


class StartInitialWorkflowResult(BaseModel):
    initial_session_id: str


@dataclass
class StartInitialWorkflow:
    """CLI 入口：接收用户自然语言指令，加载蓝图，拉起一个 Agent Session 进行需求拆解。"""

    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort
    blueprint_registry: BlueprintRegistryPort
    project_id: str

    async def execute(
        self, cmd: StartInitialWorkflowCommand
    ) -> StartInitialWorkflowResult:
        job = DispatchJob(
            id=JobId(value=uuid.uuid4()),
            status=JobStatus.PENDING
        )
        await self.job_repo.save(job=job)

        blueprint = await self.blueprint_registry.get_blueprint(
            scope_level="project" # 之前是 story, 现在统一对齐 ScopeLevel.PROJECT
        )

        result = await self.execution_trigger.trigger_session(
            job_id=job.id,
            system_prompt=blueprint.system_prompt,
            model_tier=blueprint.model_tier,
            requirement=cmd.raw_requirement,
            context_payload={"project_id": self.project_id},
        )

        job.mark_running(session_id=result.session_id)
        await self.job_repo.save(job=job)

        return StartInitialWorkflowResult(initial_session_id=str(result.session_id.value))
