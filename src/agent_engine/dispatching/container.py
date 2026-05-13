from pathlib import Path

from dependency_injector import containers
from dependency_injector.providers import Callable, Configuration, Factory

from agent_engine.dispatching.application.use_cases.execute_session import ExecuteSession
from agent_engine.dispatching.domain.services.workspace_manager import WorkspaceManager
from agent_engine.dispatching.infrastructure.adapters.claude_agent_executor_adapter import (
    ClaudeAgentExecutorAdapter,
)


class Container(containers.DeclarativeContainer):
    config: Configuration = Configuration()

    agent_executor: Factory[ClaudeAgentExecutorAdapter] = Factory(ClaudeAgentExecutorAdapter)

    root_dir: Callable[Path] = Callable(Path, config.PROJECT_ROOT)

    workspace_manager: Factory[WorkspaceManager] = Factory(
        WorkspaceManager,
        root_dir=root_dir,
    )

    execute_session: Factory[ExecuteSession] = Factory(
        ExecuteSession,
        executor=agent_executor,
        workspace_manager=workspace_manager,
    )
