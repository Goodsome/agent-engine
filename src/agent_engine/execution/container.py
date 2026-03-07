from dependency_injector.containers import DeclarativeContainer
from agent_engine.execution.infrastructure.repositories.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from dependency_injector.providers import Factory
from agent_engine.execution.infrastructure.adapters.claude_agent_gateway import (
    ClaudeAgentGateway,
)
from agent_engine.execution.application.use_cases.execute_agent_session import (
    ExecuteAgentSession,
)


class Container(DeclarativeContainer):
    claude_agent_gateway = Factory(ClaudeAgentGateway)
    sql_alchemy_session_repository = Factory(SqlAlchemySessionRepository)
    execute_agent_session = Factory(
        ExecuteAgentSession,
        agent_gateway=claude_agent_gateway,
        session_repo=sql_alchemy_session_repository,
    )
