from dependency_injector.containers import DeclarativeContainer
from dependency_injector import providers
from dependency_injector.providers import Configuration, Factory
from agent_engine.execution.infrastructure.repositories.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from agent_engine.execution.infrastructure.adapters.claude_agent_gateway import (
    ClaudeAgentGateway,
)
from agent_engine.execution.application.use_cases.execute_agent_session import (
    ExecuteAgentSession,
)


class Container(DeclarativeContainer):
    config: Configuration = providers.Configuration()
    session_factory = providers.Dependency()

    agent_gateway: Factory[ClaudeAgentGateway] = Factory(ClaudeAgentGateway)

    sql_alchemy_session_repository: Factory[SqlAlchemySessionRepository] = Factory(
        SqlAlchemySessionRepository,
        session_factory=session_factory,
    )
    execute_agent_session: Factory[ExecuteAgentSession] = Factory(
        ExecuteAgentSession,
        agent_gateway=agent_gateway,
        session_repo=sql_alchemy_session_repository,
    )
