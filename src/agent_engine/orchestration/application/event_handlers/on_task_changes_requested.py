import logging
from dataclasses import dataclass

from event_hub.integration_events import TaskChangesRequested
from agent_engine.orchestration.application.use_cases.revise_task import ReviseTask
from agent_engine.orchestration.application.use_cases.revise_task import ReviseTaskCommand

logger = logging.getLogger(__name__)


@dataclass
class OnTaskChangesRequested:
    revise_task_use_case: ReviseTask

    async def handle_changes_requested(self, event: TaskChangesRequested):
        logger.info(f"处理任务变更请求事件: {event}")
        command = ReviseTaskCommand(
            task_id=str(event.task_id),
        )
        result = await self.revise_task_use_case.execute(command)
        logger.info(f"任务重新修改完成: session_id={result.session_id}, status={result.status}")
