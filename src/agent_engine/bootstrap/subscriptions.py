import asyncio
from agent_engine.bootstrap.container import ApplicationContainer
from event_hub import TaskReady

async def register_event_subscriptions(container: ApplicationContainer) -> None:
    """注册所有的集成事件与领域事件订阅。"""
    event_hub = container.event_hub()
    if asyncio.iscoroutine(event_hub) or asyncio.isfuture(event_hub):
        event_hub = await event_hub
    
    # 任务就绪事件订阅
    on_task_ready = container.orchestration_container.on_task_ready()
    if asyncio.iscoroutine(on_task_ready) or asyncio.isfuture(on_task_ready):
        on_task_ready = await on_task_ready
        
    event_hub.register_integration(TaskReady, on_task_ready.handle_dispatch_task)
