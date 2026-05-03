import asyncio
import typer
from typing import cast
from rich.console import Console

from dependency_injector.containers import DynamicContainer
from agent_engine.bootstrap.subscriptions import register_event_subscriptions

console = Console()


async def _do_listen(
    container: DynamicContainer,
):
    _init = container.init_resources()
    assert _init is not None
    await _init
    
    await register_event_subscriptions(container) # type: ignore
    
    event_hub = container.event_hub()
    
    try:
        console.print("Starting EventHub subscriber...")
        await event_hub.start()
        await event_hub.run_forever()
    except asyncio.CancelledError:
        console.print("EventHub subscriber cancelled.")
    except Exception as e:
        console.print(f"Error in EventHub subscriber: {e}")
        raise e
    finally:
        console.print("Stopping EventHub subscriber...")
        await event_hub.stop()
        
        _shutdown = container.shutdown_resources()
        if _shutdown is not None:
            await _shutdown

def listen(ctx: typer.Context):
    """Start the long-running event listener for domain events."""
    console.print("Starting event listener process...")
    container: DynamicContainer = cast(DynamicContainer, ctx.obj)
    
    asyncio.run(_do_listen(container))
