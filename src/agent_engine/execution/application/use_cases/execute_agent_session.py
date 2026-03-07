from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from typing import Union
from pydantic import BaseModel, Field
from agent_engine.execution.domain.enums import SessionType
from agent_engine.shared.domain.value_objects.task_id import TaskId
from dataclasses import dataclass
from agent_engine.execution.domain.ports.agent_session_repository import (
    AgentSessionRepository,
)
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.execution.domain.ports.sop_repository import SopRepository
from agent_engine.shared.domain.value_objects.job_id import JobId


class ExecuteAgentSessionCommand(BaseModel):
    job_id: JobId
    task_id: TaskId | None = Field(default=None)
    requirement: str | None = Field(default=None)
    session_type: SessionType


class ExecuteAgentSessionResult(BaseModel):
    session_id: SessionId
    is_success: bool
    output: str | None = Field(default=None)


@dataclass
class ExecuteAgentSession:
    """核心用例：组装 SOP 与上下文，调用 AgentGateway 执行。这是 Orchestration 域中 ExecutionTriggerPort 的物理接收端。"""

    agent_gateway: AgentGateway
    sop_repo: SopRepository
    session_repo: AgentSessionRepository

    def execute(self, cmd: ExecuteAgentSessionCommand) -> ExecuteAgentSessionResult: ...
