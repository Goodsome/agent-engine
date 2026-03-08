import json
import uuid
from agent_engine.execution.domain.aggregates.agent_session import AgentSession
from agent_engine.execution.domain.enums import SessionStatus

from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from pydantic import BaseModel, Field
from dataclasses import dataclass
from agent_engine.execution.domain.ports.agent_session_repository import (
    AgentSessionRepository,
)
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.job_id import JobId
from typing import Any


class ExecuteAgentSessionCommand(BaseModel):
    job_id: JobId
    system_prompt: str
    requirement: str | None = Field(default=None)
    context_payload: dict[str, Any] = Field(default_factory=dict)


class ExecuteAgentSessionResult(BaseModel):
    session_id: SessionId
    is_success: bool
    output: str | None = Field(default=None)


@dataclass
class ExecuteAgentSession:
    """核心用例：接收已组装好的 system_prompt 与上下文，调用 AgentGateway 执行。这是 Orchestration 域中 ExecutionTriggerPort 的物理接收端。"""

    agent_gateway: AgentGateway
    session_repo: AgentSessionRepository

    async def execute(self, cmd: ExecuteAgentSessionCommand) -> ExecuteAgentSessionResult:
        session = AgentSession(
            id=SessionId(value=uuid.uuid4()),
            job_id=cmd.job_id,
            context_payload=cmd.context_payload,
            status=SessionStatus.IDLE
        )
        await self.session_repo.save(session=session)

        session.start()
        await self.session_repo.save(session=session)
        system_prompt = cmd.system_prompt
        if cmd.context_payload:
            system_prompt += f"\n---\ncontext_payload: {json.dumps(cmd.context_payload)}"

        try:
            output = await self.agent_gateway.run(
                system_prompt=system_prompt,
                user_prompt=cmd.requirement or "",
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
