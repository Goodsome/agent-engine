import logging
from dataclasses import dataclass

from agent_engine.orchestration.application.use_cases.handle_dispatchable_task_event import (
    HandleDispatchableTaskEvent,
)
from agent_engine.orchestration.domain.ports.domain_event_listener_port import (
    DomainEventListenerPort,
)

logger = logging.getLogger(__name__)


@dataclass
class EventListenerRunner:
    """长驻进程：持续监听领域事件并分派给对应的 Use Case"""

    listener: DomainEventListenerPort
    handle_dispatchable_task: HandleDispatchableTaskEvent
    project_id: str

    async def run(self) -> None:
        logger.info("🚀 事件监听器已启动，等待事件...")
        try:
            async for event in self.listener.listen():
                # 仅处理当前项目的事件
                if event.project_id != self.project_id:
                    logger.debug(
                        f"⏭️ 忽略其他项目的事件: {event.event_type} "
                        f"(event.project_id={event.project_id}, current={self.project_id})"
                    )
                    continue

                logger.info(
                    f"🔔 收到当前项目事件: {event.event_type} task_id={event.task_id.value}"
                )
                try:
                    result = await self.handle_dispatchable_task.execute(event)
                    logger.info(
                        f"✅ 已调度 job={result.job_id}, session={result.session_id}"
                    )
                except Exception as e:
                    logger.exception(f"❌ 处理事件失败: {e}")
        finally:
            await self.listener.close()
            logger.info("🛑 事件监听器已停止")
