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


@dataclass
class StartInitialWorkflow:
    """CLI 入口：接收用户自然语言指令，直接拉起一个 Planner Session，让 Agent 负责向 TaskGraph 写入初始节点。"""

    job_repo: DispatchJobRepository
    execution_trigger: ExecutionTriggerPort

    def execute(
        self, cmd: StartInitialWorkflowCommand
    ) -> StartInitialWorkflowResult: ...
