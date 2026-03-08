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

app = typer.Typer(help="Orchestration Context Commands")
console = Console()

@inject
def _do_tick(
    run_tick_use_case: RunEventLoopTick = Provide["orchestration_container.run_event_loop_tick"],
):
    cmd = RunEventLoopTickCommand()
    return asyncio.run(run_tick_use_case.execute(cmd))

@app.command("tick")
def tick():
    """Run a single tick of the event loop."""
    console.print("Running event loop tick...")
    result = _do_tick()
    console.print(f"Tick completed. Dispatched [bold green]{result.dispatched_count}[/bold green] jobs.")

@inject
def _do_start_workflow(
    cmd: StartInitialWorkflowCommand,
    start_workflow_use_case: StartInitialWorkflow = Provide["orchestration_container.start_initial_workflow"],
):
    return asyncio.run(start_workflow_use_case.execute(cmd))

@app.command("start-workflow")
def start_workflow(
    requirement: str = typer.Argument(..., help="The raw requirement to start the workflow"),
):
    """Start an initial workflow with a requirement."""
    console.print(f"Starting workflow with requirement: [green]{requirement}[/green]")
    cmd = StartInitialWorkflowCommand(raw_requirement=requirement)
    result = _do_start_workflow(cmd)
    console.print(f"Workflow started. Initial Session ID: [bold blue]{result.initial_session_id}[/bold blue]")

@inject
def _do_listen(
    runner: EventListenerRunner = Provide["orchestration_container.event_listener_runner"],
):
    return asyncio.run(runner.run())

@app.command("listen")
def listen():
    """Start the long-running event listener for domain events."""
    console.print("Starting event listener process...")
    _do_listen()
