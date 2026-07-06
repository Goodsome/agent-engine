import asyncio
import json
import uuid
import traceback

import typer
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from agent_engine.dispatching.application.use_cases.execute_session import ExecuteSession
from agent_engine.dispatching.application.dtos.execute_session_command import ExecuteSessionCommand
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.shared.domain.enums import ModelTier

app = typer.Typer(help="Execution Context Commands")
console = Console()

@inject
async def _do_execute_session(
    cmd: ExecuteSessionCommand,
    execute_use_case: ExecuteSession = Provide["dispatching_container.execute_session"],
):
    return await execute_use_case.execute(cmd)

def execute_session(
    user_prompt: str = typer.Argument(..., help="The user prompt"),
    project_id: str| None = typer.Option(None, "--project", help="The project ID"),
    system_prompt: str = typer.Option(None, "--system-prompt", "-p", help="The system prompt for the agent"),
    session_id: str = typer.Option(None, "--session-id", "-s", help="The session ID"),
    model_tier: ModelTier = typer.Option(ModelTier.FAST, "--tier", "-t", help="Model tier to use"),
    context: str = typer.Option(None, "--context", help="The context for the session"),
    context_payload: str = typer.Option("{}", help="JSON string of context payload"),
):
    """Execute an agent session manually."""
    try:
        payload = json.loads(context_payload)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/bold red] context_payload must be a valid JSON string.")
        raise typer.Exit(code=1)

    effective_session_id = session_id or str(uuid.uuid4())

    cmd = ExecuteSessionCommand(
        project_id=project_id,
        session_id=effective_session_id,
        system_prompt=system_prompt or "",
        user_prompt=user_prompt,
        context_payload=payload,
        model_tier=model_tier,
        context=context,
    )

    console.print(f"Executing session [bold blue]{effective_session_id}[/bold blue]")
    console.print(f"System prompt: [green]{system_prompt}[/green]")
    console.print(f"User prompt: [cyan]{cmd.user_prompt}[/cyan]")

    try:
        result = asyncio.run(_do_execute_session(cmd))
    except Exception:
        console.print("[bold red]Fatal error in execute_session:[/bold red]")
        console.print(traceback.format_exc())
        raise typer.Exit(code=1)

    if result.status == DispatchStatus.SUCCESS:
        console.print(f"[bold green]Success![/bold green] Session ID: {effective_session_id}")
        console.print(f"Output: {result.output}")
    else:
        console.print(f"[bold red]Failed![/bold red] Status: {result.status.value}")
        console.print(f"Error: {result.fault}")
