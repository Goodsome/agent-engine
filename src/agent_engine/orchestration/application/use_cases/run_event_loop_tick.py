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


@dataclass
class RunEventLoopTick:
    """核心调度循环的一帧 (Tick)：查询 READY 任务 -> 创建 DispatchJob -> 触发 Execution。"""

    task_query_port: TaskGraphQueryPort
    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort

    def execute(self, cmd: RunEventLoopTickCommand) -> RunEventLoopTickResult: ...
