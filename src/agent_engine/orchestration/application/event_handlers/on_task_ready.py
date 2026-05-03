import logging
from dataclasses import dataclass

from event_hub import TaskReady

logger = logging.getLogger(__name__)

@dataclass
class OnTaskReady:

    async def handle_dispatch_task(self, event: TaskReady):
        logger.info(f"处理任务就绪事件，准备执行任务: {event}")