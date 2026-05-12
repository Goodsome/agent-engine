import logging
from dataclasses import dataclass

from event_hub.integration_events import TaskReady
from agent_engine.orchestration.application.use_cases.dispatch_task import DispatchTask
from agent_engine.orchestration.application.dtos.dispatch_task_command import DispatchTaskCommand

logger = logging.getLogger(__name__)

@dataclass
class OnTaskReady:
    dispatch_task_use_case: DispatchTask

    async def handle_dispatch_task(self, event: TaskReady):
        logger.info(f"处理任务就绪事件，准备执行任务: {event.task_id}")
        context_payload = {
            "task_id": str(event.task_id),
            "project_id": str(event.project_id),
            "scope_level": event.scope_level,
            "bounded_context": event.bounded_context,
            "architecture_layer": event.architecture_layer,
        }
        
        # 将外部事件转化为内部指令
        command = DispatchTaskCommand(
            task_id=str(event.task_id),
            project_id=str(event.project_id),
            scope_level=event.scope_level,
            context_payload=context_payload,
            architecture_layer=event.architecture_layer,
        )
        
        result = await self.dispatch_task_use_case.execute(command)
        logger.info(f"任务执行完成: session_id={result.session_id}, status={result.status}")
