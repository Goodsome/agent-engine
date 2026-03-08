from dependency_injector import containers, providers

from agent_engine.config import get_settings
from agent_engine.execution.container import Container as ExecutionContainer
from agent_engine.orchestration.container import Container as OrchestrationContainer
from agent_engine.shared.infrastructure.database import (
    create_db_engine,
    create_session_factory,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """
    组合根 (Composition Root) 容器
    负责初始化共享的基础设施并将其注入到各个子上下文中
    """

    config = providers.Configuration()

    # 初始化共享的数据库引擎
    db_engine = providers.Singleton(
        create_db_engine,
        db_url=config.database_url,
    )

    # 创建数据库会话工厂
    session_factory = providers.Singleton(
        create_session_factory,
        engine=db_engine,
    )

    # 组装 Execution 限界上下文容器
    execution_container = providers.Container(
        ExecutionContainer,
        session_factory=session_factory,
    )

    # 组装 Orchestration 限界上下文容器
    orchestration_container = providers.Container(
        OrchestrationContainer,
        session_factory=session_factory,
    )


def bootstrap() -> ApplicationContainer:
    """
    引导程序：加载配置并构建全局容器
    """
    settings = get_settings()

    container = ApplicationContainer()
    
    # 将 Pydantic Settings 中的值加载到 DI 配置中
    container.config.from_pydantic(settings)
    
    # 处理 PostgresDsn 对象 (如果存在)，转成字符串给数据库引擎用
    if settings.DATABASE_URL:
        container.config.database_url.override(str(settings.DATABASE_URL))
    else:
        # 如果没有配置数据库，给一个默认的内存 SQLite 用来保证不报错 (或者也可以抛错)
        container.config.database_url.override("sqlite+aiosqlite:///:memory:")

    return container
