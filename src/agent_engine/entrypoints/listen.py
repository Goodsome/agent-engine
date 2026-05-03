import typer
import asyncio
import logging
import inspect
from agent_engine.bootstrap.container import ApplicationContainer
from agent_engine.bootstrap.subscriptions import bind_all_subscriptions

app = typer.Typer(name="AgentEngine")
logger = logging.getLogger(__name__)


async def async_listen_loop(container: ApplicationContainer) -> None:
    """异步的监听主循环逻辑"""
    init_task = container.init_resources()
    if inspect.isawaitable(init_task):
        await init_task
            
    event_hub = container.event_hub()
    
    try:
        await bind_all_subscriptions(container)
        
        # 1. 显式启动 Redis 消费线程和连接池
        logger.info("🚀 正在启动 Agent Engine 事件监听器...")
        await event_hub.start()
        
        logger.info("🎧 监听中... (按 Ctrl+C 优雅退出)")
        # 2. 阻塞在此，直到收到停止信号
        await event_hub.run_forever()
        
    except asyncio.CancelledError:
        logger.info("🛑 收到外部取消信号...")
    finally:
        # 3. 确保优雅停机，ACK 处理完当前消息
        logger.info("⏳ 正在安全关闭连接...")
        await event_hub.stop()
        logger.info("👋 Agent Engine 退出完毕。")


def listen(ctx: typer.Context):
    """启动常驻后台的 Agent 事件消费监听器"""
    container = ctx.obj
    
    try:
        # 启动纯异步的消费循环
        asyncio.run(async_listen_loop(container))
    except KeyboardInterrupt:
        # 捕获用户的 Ctrl+C 动作
        logger.info("收到中止指令 (KeyboardInterrupt)。")
    finally:
        # 关闭依赖注入容器中的其他资源（如DB连接）
        container.shutdown_resources()
