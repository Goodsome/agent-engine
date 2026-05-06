from dependency_injector import containers
from dependency_injector.providers import Factory, Configuration
from agent_engine.dispatching.infrastructure.adapters.claude_agent_executor_adapter import (
    ClaudeAgentExecutorAdapter,
)
from agent_engine.dispatching.application.use_cases.execute_session import (
    ExecuteSession,
)


class Container(containers.DeclarativeContainer):
    config: Configuration = Configuration()

    agent_executor: Factory[ClaudeAgentExecutorAdapter] = Factory(ClaudeAgentExecutorAdapter)

    execute_session: Factory[ExecuteSession] = Factory(
        ExecuteSession,
        executor=agent_executor,
    )
