from dependency_injector import containers, providers
from dependency_injector.providers import Factory
from agent_engine.dispatching.infrastructure.adapters.claude_agent_executor import (
    ClaudeAgentExecutorAdapter,
)
from agent_engine.dispatching.application.use_cases.handle_dispatch_command import (
    HandleDispatchCommand,
)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    agent_executor = Factory(ClaudeAgentExecutorAdapter)

    handle_dispatch_command = Factory(
        HandleDispatchCommand,
        executor=agent_executor,
    )
