import asyncio
import typer
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from agent_engine.orchestration.application.use_cases.run_event_loop_tick import (
    RunEventLoopTick,
    RunEventLoopTickCommand,
)
from agent_engine.orchestration.application.use_cases.start_initial_workflow import (
    StartInitialWorkflow,
    StartInitialWorkflowCommand,
)

from agent_engine.orchestration.interfaces.event_listener import EventListenerRunner

console = Console()

@inject
async def _do_tick(
    run_tick_use_case: RunEventLoopTick = Provide["orchestration_container.run_event_loop_tick"],
):
    cmd = RunEventLoopTickCommand()
    return await run_tick_use_case.execute(cmd)

def tick():
    """Run a single tick of the event loop."""
    console.print("Running event loop tick...")
    result = asyncio.run(_do_tick())
    console.print(f"Tick completed. Dispatched [bold green]{result.dispatched_count}[/bold green] jobs.")

@inject
async def _do_start_workflow(
    cmd: StartInitialWorkflowCommand,
    start_workflow_use_case: StartInitialWorkflow = Provide["orchestration_container.start_initial_workflow"],
):
    return await start_workflow_use_case.execute(cmd)

def start_workflow(
    requirement: str = typer.Argument(..., help="The raw requirement to start the workflow"),
):
    """Start an initial workflow with a requirement."""
    console.print(f"Starting workflow with requirement: [green]{requirement}[/green]")
    cmd = StartInitialWorkflowCommand(raw_requirement=requirement)
    result = asyncio.run(_do_start_workflow(cmd))
    console.print(f"Workflow started. Initial Session ID: [bold blue]{result.initial_session_id}[/bold blue]")

from dependency_injector.containers import DynamicContainer

@inject
async def _do_listen(
    container: DynamicContainer,
):
    print(f"--- 探针 1: 成功进入 _do_listen ---")
    await container.init_resources()
    
    try:
        print("--- 探针 3: 准备调用 runner.run() ---")
        runner = await container.orchestration_container.event_listener_runner()
        
        await runner.run()
    except Exception as e:
        print(f"--- 探针 4: 发生严重错误: {repr(e)} ---")
        raise
    finally:
        await container.shutdown_resources()

def listen(ctx: typer.Context):
    """Start the long-running event listener for domain events."""
    console.print("Starting event listener process...")
    container: DynamicContainer = ctx.obj
    
    asyncio.run(_do_listen(container))
