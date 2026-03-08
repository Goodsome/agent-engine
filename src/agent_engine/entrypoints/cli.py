import typer
from agent_engine.bootstrap import bootstrap
from agent_engine.execution.interfaces.cli import app as execution_app
from agent_engine.orchestration.interfaces.cli import app as orchestration_app

app = typer.Typer(
    name="agent-engine",
    help="Agent Engine CLI",
    add_completion=False,
)

app.add_typer(execution_app, name="execution")
app.add_typer(orchestration_app, name="orchestration")

def main():
    # Bootstrap the DI container
    container = bootstrap()
    
    # Wire the container to the CLI modules
    container.wire(modules=[
        "agent_engine.execution.interfaces.cli",
        "agent_engine.orchestration.interfaces.cli",
    ])
    
    app()

if __name__ == "__main__":
    main()
