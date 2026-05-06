from dataclasses import dataclass

from agent_engine.agent_registry.application.ports.agent_profile_query_service import AgentProfileQueryService
from agent_engine.dispatching.application.use_cases.execute_session import ExecuteSession, ExecuteSessionCommand
from agent_engine.orchestration.domain.ports.agent_session_repository import AgentSessionRepository
from agent_engine.orchestration.domain.aggregates.agent_session import AgentSession
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.project_id import ProjectId
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.orchestration.domain.enums import SessionStatus
from agent_engine.agent_registry.application.dtos.agent_profile import AgentProfile

from pydantic import BaseModel, Field


class DispatchTaskCommand(BaseModel):
    """调度任务指令：描述了要由哪个 Agent 执行哪个任务"""
    task_id: str
    project_id: str
    scope_level: str
    architecture_layer: str | None = None
    context_payload: dict[str, str | None] = Field(default_factory=dict)


class DispatchTaskResult(BaseModel):
    """调度任务结果 DTO"""
    session_id: str
    status: str
    output: str | None = None
    fault: str | None = None


@dataclass
class DispatchTask:
    """Orchestration 应用层用例：调度任务执行"""

    agent_profile_query_service: AgentProfileQueryService
    execute_session_use_case: ExecuteSession
    session_repository: AgentSessionRepository

    async def execute(self, command: DispatchTaskCommand) -> DispatchTaskResult:
        # 1. 获取 Agent Profile
        profile = self.agent_profile_query_service.get_profile(
            command.scope_level,
            architecture_layer=command.architecture_layer
        )
        
        # 2. 拼成 system_prompt
        system_prompt = self._build_system_prompt(profile)
        user_prompt = f"执行任务：{command.task_id}"
        
        # 3. 创建 AgentSession
        session_id = SessionId.create()
        session = AgentSession(
            id=session_id,
            task_id=TaskId.reconstitute(command.task_id),
            project_id=ProjectId(value=command.project_id),
            status=SessionStatus.PROCESSING,
            context_payload=command.context_payload,
            system_prompt=system_prompt
        )
        session.add_user_message(user_prompt)
        await self.session_repository.save(session)
        
        # 4. 调用 ExecuteSession
        exec_command = ExecuteSessionCommand(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            session_id=str(session_id),
            project_id=command.project_id,
            context_payload=command.context_payload
        )
        
        exec_result = await self.execute_session_use_case.execute(exec_command)
        session.add_agent_message(content=exec_result.output or "")
        
        # 5. 更新 Session 状态
        session.status = SessionStatus.IDLE
            
        await self.session_repository.save(session)
        
        return DispatchTaskResult(
            session_id=str(session_id),
            status=session.status.value,
            output=exec_result.output,
            fault=exec_result.fault
        )

    def _build_system_prompt(self, profile: AgentProfile) -> str:
        prompt_parts = [
            f"You are {profile.role_name}.",
            profile.description,
            profile.role_prompt,
        ]
        if profile.rules:
            prompt_parts.append("\nSPECIFIC_RULES:")
            for key, val in profile.rules.items():
                prompt_parts.append(f"- {key}: {val}")
        return "\n".join(prompt_parts)
