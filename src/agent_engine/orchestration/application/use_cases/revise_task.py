import logging
from dataclasses import dataclass

from agent_engine.orchestration.application.dtos.revise_task import ReviseTaskCommand, ReviseTaskResult
from agent_engine.orchestration.domain.ports.agent_session_repository import AgentSessionRepository
from agent_engine.dispatching.application.use_cases.execute_session import ExecuteSession, ExecuteSessionCommand
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.orchestration.domain.enums import SessionStatus

logger = logging.getLogger(__name__)


@dataclass
class ReviseTask:
    """Orchestration 应用层用例：任务审核不通过，重新修改"""

    session_repository: AgentSessionRepository
    execute_session_use_case: ExecuteSession

    async def execute(self, command: ReviseTaskCommand) -> ReviseTaskResult:
        session = await self.session_repository.find_by_task_id(
            TaskId.reconstitute(command.task_id)
        )

        if session is None:
            logger.warning(f"未找到 task_id={command.task_id} 对应的 Session")
            return ReviseTaskResult(
                status="failed",
                fault=f"Session not found for task_id={command.task_id}",
            )

        user_prompt = f"任务审核不通过，重新领取任务修改：{command.task_id}"

        session.add_user_message(content=user_prompt)
        session.status = SessionStatus.PROCESSING
        await self.session_repository.save(session)

        exec_command = ExecuteSessionCommand(
            system_prompt="",
            user_prompt=user_prompt,
            session_id=str(session.id),
            project_id=str(session.project_id),
            context_payload={},
        )

        exec_result = await self.execute_session_use_case.execute(exec_command)

        session.add_agent_message(content=exec_result.output or "")
        session.status = SessionStatus.IDLE
        await self.session_repository.save(session)

        return ReviseTaskResult(
            session_id=str(session.id),
            status=exec_result.status.value,
            output=exec_result.output,
            fault=exec_result.fault,
        )
