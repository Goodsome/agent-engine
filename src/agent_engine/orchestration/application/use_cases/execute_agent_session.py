import uuid
from typing import Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

from agent_engine.orchestration.domain.aggregates.agent_session import AgentSession
from agent_engine.orchestration.domain.enums import SessionStatus
from agent_engine.orchestration.domain.ports.agent_session_repository import AgentSessionRepository
from agent_engine.dispatching.application.use_cases.handle_dispatch_command import HandleDispatchCommand
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.dispatching.domain.value_objects.dispatch_command import DispatchCommand
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.enums import ModelTier


class ExecuteAgentSessionCommand(BaseModel):
    job_id: JobId
    system_prompt: str
    requirement: str | None = Field(default=None)
    context_payload: dict[str, Any] = Field(default_factory=dict)
    model_tier: ModelTier | None = Field(default=None)


class ExecuteAgentSessionResult(BaseModel):
    session_id: SessionId
    is_success: bool
    output: str | None = Field(default=None)


@dataclass
class ExecuteAgentSession:
    """Orchestration 域的用例：管理 AgentSession 状态，并调用 Dispatching 域执行具体指令。"""

    dispatch_handler: HandleDispatchCommand
    session_repo: AgentSessionRepository

    async def execute(self, cmd: ExecuteAgentSessionCommand) -> ExecuteAgentSessionResult:
        # 1. 创建并持久化 Session (Orchestration 职责)
        session = AgentSession(
            id=SessionId(value=uuid.uuid4()),
            job_id=cmd.job_id,
            context_payload=cmd.context_payload,
            status=SessionStatus.IDLE
        )
        await self.session_repo.save(session=session)

        # 2. 状态变更为 RUNNING
        session.start()
        await self.session_repo.save(session=session)

        # 3. 构造指令并下发至 Dispatching (跨上下文调用)
        dispatch_cmd = DispatchCommand(
            system_prompt=cmd.system_prompt,
            user_prompt=cmd.requirement or "",
            session_id=str(session.id.value),
            model_tier=cmd.model_tier,
            context_payload=cmd.context_payload
        )
        
        receipt = await self.dispatch_handler.execute(dispatch_cmd)

        # 4. 根据回执更新 Session 状态
        if receipt.status == DispatchStatus.SUCCESS:
            session.finish_with_success(output=receipt.output or "")
            is_success = True
        else:
            session.finish_with_error(error=receipt.fault or "Unknown error")
            is_success = False
        
        await self.session_repo.save(session=session)

        return ExecuteAgentSessionResult(
            session_id=session.id,
            is_success=is_success,
            output=receipt.output
        )
