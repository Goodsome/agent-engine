from dependency_injector.containers import DeclarativeContainer
from dependency_injector import providers
from dependency_injector.providers import Factory
from agent_engine.orchestration.infrastructure.repositories.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from agent_engine.orchestration.application.use_cases.dispatch_task import DispatchTask
from agent_engine.orchestration.application.event_handlers.on_task_ready import OnTaskReady


class Container(DeclarativeContainer):
    config = providers.Configuration()
    session_factory = providers.Dependency()
    
    # 外部依赖
    execute_session = providers.Dependency()
    blueprint_registry = providers.Dependency()
    agent_profile_query_service = providers.Dependency()
    
    sql_alchemy_session_repository = Factory(
        SqlAlchemySessionRepository,
        session_factory=session_factory,
    )

    dispatch_task = Factory(
        DispatchTask,
        agent_profile_query_service=agent_profile_query_service,
        execute_session_use_case=execute_session,
        session_repository=sql_alchemy_session_repository,
    )
    
    on_task_ready = Factory(
        OnTaskReady,
        dispatch_task_use_case=dispatch_task,
    )
