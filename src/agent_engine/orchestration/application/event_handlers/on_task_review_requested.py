import logging
from dataclasses import dataclass

from event_hub.integration_events import TaskReviewRequested
from agent_engine.orchestration.application.use_cases.review_task import ReviewTask
from agent_engine.orchestration.application.use_cases.review_task import ReviewTaskCommand

logger = logging.getLogger(__name__)


@dataclass
class OnTaskReviewRequested:
    review_task_use_case: ReviewTask

    async def handle_review_task(self, event: TaskReviewRequested):
        logger.info(f"处理任务评审请求事件: {event}")
        command = ReviewTaskCommand(
            task_id=str(event.task_id),
            parent_id=event.parent_id,
        )
        result = await self.review_task_use_case.execute(command)
        logger.info(f"任务评审完成: session_id={result.session_id}, status={result.status}")
