import logging

from agent_engine.bootstrap.container import ApplicationContainer
from event_hub import EventHub, TaskReady


logger = logging.getLogger(__name__)

async def bind_all_subscriptions(container: ApplicationContainer) -> None:
    event_hub: EventHub = container.event_hub()
    logger.info("注册消费订阅...")
    
    # 注册跨进程的集成事件
    on_task_ready = await container.orchestration_container.on_task_ready()
    
    logger.info("注册消费订阅....")
    event_hub.register_integration(TaskReady, on_task_ready.handle_dispatch_task)

