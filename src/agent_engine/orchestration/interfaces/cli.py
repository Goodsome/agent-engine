import asyncio
import typer
from typing import Annotated, cast
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from agent_engine.orchestration.interfaces.event_listener import EventListenerRunner
from dependency_injector.containers import DynamicContainer

console = Console()


async def _do_listen(
    container: DynamicContainer,
):
    _init = container.init_resources()
    assert _init is not None
    await _init
    
    try:
        orchestration_container = container.orchestration_container
        runner: EventListenerRunner = await orchestration_container.event_listener_runner()
        
        await runner.run()
    except Exception as e:
        raise e
    finally:
        _shutdown = container.shutdown_resources()
        if _shutdown is not None:
            await _shutdown

def listen(ctx: typer.Context):
    """Start the long-running event listener for domain events."""
    console.print("Starting event listener process...")
    container: DynamicContainer = cast(DynamicContainer, ctx.obj)
    
    asyncio.run(_do_listen(container))
