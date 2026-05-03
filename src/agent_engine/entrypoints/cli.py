import typer
from agent_engine.bootstrap import create_container, setup_cli_logging
from agent_engine.dispatching.interfaces.cli import execute_session
from agent_engine.orchestration.interfaces.cli import (
    listen,
    start_workflow,
)
from agent_engine.integration.interfaces.cli import feishu_listen

def create_app():
    app = typer.Typer(
        name="agent-engine",
        help="Agent Engine CLI",
        add_completion=False,
    )
    container = create_container(init_resources=False)
    container.wire(modules=[
        "agent_engine.dispatching.interfaces.cli",
        "agent_engine.orchestration.interfaces.cli",
        "agent_engine.integration.interfaces.cli",
    ])
    
    @app.callback()
    def global_setup(ctx: typer.Context):
        ctx.obj = container
        

    app.command(name="execute-session")(execute_session)
    app.command(name="listen")(listen)
    app.command(name="start-workflow")(start_workflow)
    app.command(name="feishu-listen")(feishu_listen)
    
    return app


def main():
    logger = setup_cli_logging()
    logger.info("Starting Agent Engine CLI")
    app = create_app()
    app()

if __name__ == "__main__":
    main()
