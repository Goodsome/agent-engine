import asyncio
import json
from pathlib import Path
import uuid
import traceback
from typing import Annotated

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
    user_prompt: Annotated[str, typer.Argument(help="The user prompt")],
    project_id: Annotated[str | None, typer.Option("--project", help="The project ID")] = None,
    system_prompt: Annotated[str | None, typer.Option("--system-prompt", "-p", help="The system prompt for the agent")] = None,
    session_id: Annotated[str | None, typer.Option("--session-id", "-s", help="The session ID")] = None,
    model_tier: Annotated[ModelTier, typer.Option("--tier", "-t", help="Model tier to use")] = ModelTier.FAST,
    context: Annotated[str | None, typer.Option("--context", help="The context for the session")] = None,
    context_payload: Annotated[str, typer.Option(help="JSON string of context payload")] = "{}",
    system_prompt_file: Annotated[Path | None, typer.Option("--system-prompt-file", help="The system prompt file path for the agent")] = None,
):
    """Execute an agent session manually."""
    try:
        payload = json.loads(context_payload)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/bold red] context_payload must be a valid JSON string.")
        raise typer.Exit(code=1)

    effective_session_id = session_id or str(uuid.uuid4())

    if system_prompt_file:
        if not system_prompt_file.exists():
            typer.echo(f"Error: System prompt file not found at {system_prompt_file}", err=True)
            raise typer.Exit(code=1)
        actual_system_prompt = system_prompt_file.read_text(encoding="utf-8")
    else:
        actual_system_prompt = system_prompt or ""

    cmd = ExecuteSessionCommand(
        project_id=project_id,
        session_id=effective_session_id,
        system_prompt=actual_system_prompt,
        user_prompt=user_prompt,
        context_payload=payload,
        model_tier=model_tier,
        context=context,
    )

    # console.print(f"Executing session [bold blue]{effective_session_id}[/bold blue]")
    # console.print(f"System prompt: [green]{actual_system_prompt}[/green]")
    # console.print(f"User prompt: [cyan]{cmd.user_prompt}[/cyan]")

    try:
        result = asyncio.run(_do_execute_session(cmd))
    except Exception:
        console.print("[bold red]Fatal error in execute_session:[/bold red]")
        console.print(traceback.format_exc())
        raise typer.Exit(code=1)

    if result.status == DispatchStatus.SUCCESS:
        # console.print(f"[bold green]Success![/bold green] Session ID: {effective_session_id}")
        console.print(f"{result.output}")
    else:
        # console.print(f"[bold red]Failed![/bold red] Status: {result.status.value}")
        console.print(f"Error: {result.fault}")
