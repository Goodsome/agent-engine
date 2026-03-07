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


import uuid
from agent_engine.execution.domain.aggregates.agent_session import AgentSession
from agent_engine.execution.domain.enums import SessionStatus

@dataclass
class ExecuteAgentSession:
    """核心用例：组装 SOP 与上下文，调用 AgentGateway 执行。这是 Orchestration 域中 ExecutionTriggerPort 的物理接收端。"""

    agent_gateway: AgentGateway
    sop_repo: SopRepository
    session_repo: AgentSessionRepository

    async def execute(self, cmd: ExecuteAgentSessionCommand) -> ExecuteAgentSessionResult:
        session = AgentSession(
            id=SessionId(value=uuid.uuid4()),
            job_id=cmd.job_id,
            task_id=cmd.task_id,
            session_type=cmd.session_type,
            context_payload={"requirement": cmd.requirement} if cmd.requirement else {},
            status=SessionStatus.IDLE
        )
        await self.session_repo.save(session=session)

        session.start()
        await self.session_repo.save(session=session)

        sop = await self.sop_repo.get_sop(session_type=cmd.session_type)

        try:
            output = await self.agent_gateway.run(
                system_prompt=sop,
                user_prompt=cmd.requirement or "Please execute your task.",
                tools=[]
            )
            session.finish_with_success(output=output)
            is_success = True
        except Exception as e:
            output = str(e)
            session.finish_with_error(error=output)
            is_success = False

        await self.session_repo.save(session=session)

        return ExecuteAgentSessionResult(
            session_id=session.id,
            is_success=is_success,
            output=session.final_output if is_success else session.error_message
        )
