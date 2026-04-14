"""
Root DI container for the entire application.
Aggregates all bounded context containers and provides shared dependencies.
纯声明式设计：只描述依赖关系，不包含任何配置数据和实例化逻辑。
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from dependency_injector import containers, providers
from dependency_injector.containers import WiringConfiguration
from dependency_injector.providers import Configuration, Container, Singleton
from agent_engine.execution.container import Container as ExecutionContainer
from agent_engine.orchestration.container import Container as OrchestrationContainer
from agent_engine.integration.container import Container as IntegrationContainer
from agent_engine.shared.infrastructure.database import (
    init_database,
    Database,
)

def _get_session_factory(db: Database) -> async_sessionmaker[AsyncSession]:
    return db.session_factory


class ApplicationContainer(containers.DeclarativeContainer):
    """Root application container that composes all context containers."""

    # Wiring configuration - add packages where dependencies need to be injected
    wiring_config: WiringConfiguration = containers.WiringConfiguration(
        packages=[
            "agent_engine.orchestration.interfaces",
            "agent_engine.execution.interfaces",
            "agent_engine.integration.interfaces",
        ]
    )

    # 顶层全局配置树
    config: Configuration = providers.Configuration()

    # 初始化共享的数据库资源（包含生命周期管理）
    db: providers.Resource[Database] = providers.Resource(
        init_database,
        connection_string=config.DATABASE_URL,
    )

    # 数据库会话工厂
    session_factory: Singleton[async_sessionmaker[AsyncSession]] = providers.Singleton(
        _get_session_factory,
        db=db,
    )

    # 组装 Execution 限界上下文容器
    execution_container: Container[ExecutionContainer] = providers.Container(
        ExecutionContainer,
        config=config,
        session_factory=session_factory,
    )

    # 组装 Orchestration 限界上下文容器
    orchestration_container: Container[OrchestrationContainer] = providers.Container(
        OrchestrationContainer,
        config=config,
        session_factory=session_factory,
        execute_agent_session=execution_container.execute_agent_session,
    )

    # 组装 Integration 限界上下文容器
    integration_container: Container[IntegrationContainer] = providers.Container(
        IntegrationContainer,
        config=config,
        session_factory=session_factory,
        execution_trigger=orchestration_container.in_process_execution_trigger,
    )


__all__ = ["ApplicationContainer"]
