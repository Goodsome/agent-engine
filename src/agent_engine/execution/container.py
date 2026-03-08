from dependency_injector.containers import DeclarativeContainer
from dependency_injector import providers
from agent_engine.execution.infrastructure.repositories.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from dependency_injector.providers import Factory
from agent_engine.execution.infrastructure.adapters.claude_agent_gateway import (
    ClaudeAgentGateway,
)
from agent_engine.execution.infrastructure.adapters.gemini_agent_gateway import (
    GeminiAgentGateway,
)
from agent_engine.execution.infrastructure.adapters.agent_gateway_router import (
    AgentGatewayRouter,
)
from agent_engine.execution.application.use_cases.execute_agent_session import (
    ExecuteAgentSession,
)


class Container(DeclarativeContainer):
    config = providers.Configuration()
    session_factory = providers.Dependency()

    claude_agent_gateway = Factory(ClaudeAgentGateway)
    gemini_agent_gateway = Factory(GeminiAgentGateway)

    # 动态路由网关，根据 model 参数选择底层实现
    agent_gateway = Factory(
        AgentGatewayRouter,
        claude_gateway=claude_agent_gateway,
        gemini_gateway=gemini_agent_gateway,
        default_provider=config.AGENT_PROVIDER,
    )

    sql_alchemy_session_repository = Factory(
        SqlAlchemySessionRepository,
        session_factory=session_factory,
    )
    execute_agent_session = Factory(
        ExecuteAgentSession,
        agent_gateway=agent_gateway,
        session_repo=sql_alchemy_session_repository,
    )
