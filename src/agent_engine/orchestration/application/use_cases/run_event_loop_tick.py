from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.orchestration.domain.ports.dispatch_job_repository import (
    DispatchJobRepository,
)
from pydantic import BaseModel
from agent_engine.orchestration.domain.ports.task_graph_query_port import (
    TaskGraphQueryPort,
)
from dataclasses import dataclass


class RunEventLoopTickCommand(BaseModel): ...


class RunEventLoopTickResult(BaseModel):
    dispatched_count: int


import uuid
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus
from agent_engine.shared.domain.value_objects.job_id import JobId

@dataclass
class RunEventLoopTick:
    """核心调度循环的一帧 (Tick)：查询 READY 任务 -> 创建 DispatchJob -> 触发 Execution。"""

    task_query_port: TaskGraphQueryPort
    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort

    def execute(self, cmd: RunEventLoopTickCommand) -> RunEventLoopTickResult:
        tasks = self.task_query_port.fetch_ready_tasks()
        dispatched_count = 0

        for task in tasks:
            job = DispatchJob(
                id=JobId(value=uuid.uuid4()),
                task_id=task.task_id,
                status=JobStatus.PENDING
            )
            self.job_repo.save(job=job)

            session_id = self.execution_trigger.trigger_session(
                job_id=job.id,
                task_id=task.task_id,
                requirement=task.intent or task.name
            )

            job.mark_running(session_id=session_id)
            self.job_repo.save(job=job)
            dispatched_count += 1

        return RunEventLoopTickResult(dispatched_count=dispatched_count)
