import asyncio
import json
import uuid

import typer
from rich.console import Console
from dependency_injector.wiring import Provide, inject

from agent_engine.execution.application.use_cases.execute_agent_session import (
    ExecuteAgentSession,
    ExecuteAgentSessionCommand,
)
from agent_engine.shared.domain.value_objects.job_id import JobId

app = typer.Typer(help="Execution Context Commands")
console = Console()

@inject
def _do_execute_session(
    cmd: ExecuteAgentSessionCommand,
    execute_use_case: ExecuteAgentSession = Provide["execution_container.execute_agent_session"],
):
    return asyncio.run(execute_use_case.execute(cmd))

def execute_session(
    system_prompt: str = typer.Argument(..., help="The system prompt for the agent"),
    requirement: str = typer.Option(None, "--requirement", "-r", help="The user requirement"),
    context_payload: str = typer.Option("{}", "--context", "-c", help="JSON string of context payload"),
):
    """Execute an agent session manually."""
    try:
        payload = json.loads(context_payload)
    except json.JSONDecodeError:
        console.print("[bold red]Error:[/bold red] context_payload must be a valid JSON string.")
        raise typer.Exit(code=1)

    cmd = ExecuteAgentSessionCommand(
        job_id=JobId(value=uuid.uuid4()),
        system_prompt=system_prompt,
        requirement=requirement,
        context_payload=payload,
    )
    
    console.print(f"Executing session with system prompt: [green]{system_prompt}[/green]")
    
    result = _do_execute_session(cmd)
    
    if result.is_success:
        console.print(f"[bold green]Success![/bold green] Session ID: {result.session_id.value}")
        console.print(f"Output: {result.output}")
    else:
        console.print(f"[bold red]Failed![/bold red] Session ID: {result.session_id.value}")
        console.print(f"Error: {result.output}")
