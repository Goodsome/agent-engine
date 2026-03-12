"""Integration context CLI interface.

Provides command-line interface for Feishu integration:
- feishu-listen: Start the WebSocket listener for Feishu messages
"""

import asyncio
import typer
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from agent_engine.integration.application.use_cases.handle_feishu_message import (
    HandleFeishuMessage,
    HandleFeishuMessageCommand,
)
from agent_engine.integration.infrastructure.adapters.lark_ws_client import LarkWsClient

console = Console()


@inject
async def _do_feishu_listen(
    lark_client: LarkWsClient = Provide["integration_container.lark_ws_client"],
    handle_feishu_message: HandleFeishuMessage = Provide[
        "integration_container.handle_feishu_message"
    ],
):
    """内部异步函数: 设置消息处理器并启动监听器"""

    async def message_handler(payload):
        """异步消息处理器"""
        try:
            console.print(f"[blue]收到消息[/blue] chat_id={payload.chat_id}")
            result = await handle_feishu_message.execute(
                HandleFeishuMessageCommand(payload=payload)
            )
            console.print(f"[green]消息已处理[/green] session_id={result.session_id}")
        except Exception as e:
            console.print(f"[red]处理消息失败: {e}[/red]")

    lark_client.set_message_handler(message_handler)

    console.print("[bold cyan]启动飞书消息监听器...[/bold cyan]")
    console.print("按 Ctrl+C 停止监听")

    try:
        await lark_client.start_listener()
    except KeyboardInterrupt:
        console.print("\n[yellow]监听器已停止[/yellow]")


def feishu_listen():
    """Start the Feishu WebSocket listener for incoming messages.

    此命令使用异步模式，通过 run_in_executor 解决 lark-oapi SDK
    同步 WebSocket 客户端与 asyncio.run() 的事件循环冲突问题。
    """
    try:
        asyncio.run(_do_feishu_listen())
    except KeyboardInterrupt:
        console.print("\n[yellow]监听器已停止[/yellow]")