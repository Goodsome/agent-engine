import typer
from agent_engine.bootstrap import bootstrap
from agent_engine.execution.interfaces.cli import execute_session
from agent_engine.orchestration.interfaces.cli import (
    listen,
    start_workflow,
    tick,
)
from agent_engine.integration.interfaces.cli import feishu_listen

app = typer.Typer(
    name="agent-engine",
    help="Agent Engine CLI",
    add_completion=False,
)

app.command(name="execute-session")(execute_session)
app.command(name="listen")(listen)
app.command(name="start-workflow")(start_workflow)
app.command(name="tick")(tick)
app.command(name="feishu-listen")(feishu_listen)


def main():
    # Bootstrap the DI container
    container = bootstrap()

    # Wire the container to the CLI modules
    container.wire(modules=[
        "agent_engine.execution.interfaces.cli",
        "agent_engine.orchestration.interfaces.cli",
        "agent_engine.integration.interfaces.cli",
    ])

    app()

if __name__ == "__main__":
    main()
