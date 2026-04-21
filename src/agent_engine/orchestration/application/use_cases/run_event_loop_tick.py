import uuid
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from agent_engine.agent_registry.domain.ports.blueprint_registry import BlueprintRegistryPort
from pydantic import BaseModel
from agent_engine.orchestration.domain.ports.task_graph_query_port import (
    TaskGraphQueryPort,
)
from dataclasses import dataclass


class RunEventLoopTickCommand(BaseModel): ...


class RunEventLoopTickResult(BaseModel):
    dispatched_count: int


@dataclass
class RunEventLoopTick:
    """核心调度循环的一帧 (Tick)：查询 READY 任务 -> 加载对应蓝图 -> 创建 DispatchJob -> 触发 Execution。"""

    task_query_port: TaskGraphQueryPort
    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort
    blueprint_registry: BlueprintRegistryPort

    async def execute(self, cmd: RunEventLoopTickCommand) -> RunEventLoopTickResult:
        tasks = await self.task_query_port.fetch_ready_tasks()
        dispatched_count = 0

        for task in tasks:
            job = DispatchJob(
                id=JobId(value=uuid.uuid4()),
                task_id=task.task_id,
                status=JobStatus.PENDING
            )
            await self.job_repo.save(job=job)

            blueprint = await self.blueprint_registry.get_blueprint(
                scope_level=task.planning_level, # 映射逻辑可能需要后续对齐，目前保留原样
            )

            result = await self.execution_trigger.trigger_session(
                job_id=job.id,
                system_prompt=blueprint.system_prompt,
                model_tier=blueprint.model_tier,
                requirement=f"执行任务: {task.task_id}",
                context_payload={"task_id": str(task.task_id.value)},
            )

            job.mark_running(session_id=result.session_id)
            await self.job_repo.save(job=job)
            dispatched_count += 1

        return RunEventLoopTickResult(dispatched_count=dispatched_count)
