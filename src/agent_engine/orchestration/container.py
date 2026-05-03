from agent_engine.orchestration.infrastructure.repositories.sql_alchemy_dispatch_job_repository import (
    SqlAlchemyDispatchJobRepository,
)
from dependency_injector.containers import DeclarativeContainer
from dependency_injector import providers
from dependency_injector.providers import Factory
from agent_engine.orchestration.infrastructure.adapters.in_process_execution_trigger import (
    InProcessExecutionTrigger,
)
from agent_engine.orchestration.infrastructure.repositories.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from agent_engine.orchestration.application.use_cases.execute_agent_session import (
    ExecuteAgentSession,
)
from agent_engine.orchestration.application.event_handlers.on_task_ready import OnTaskReady


class Container(DeclarativeContainer):
    config = providers.Configuration()
    session_factory = providers.Dependency()
    
    # 外部依赖
    execute_session = providers.Dependency()
    blueprint_registry = providers.Dependency()

    sql_alchemy_dispatch_job_repository = Factory(
        SqlAlchemyDispatchJobRepository,
        session_factory=session_factory,
    )
    
    sql_alchemy_session_repository = Factory(
        SqlAlchemySessionRepository,
        session_factory=session_factory,
    )
    
    execute_agent_session = Factory(
        ExecuteAgentSession,
        dispatch_handler=execute_session,
        session_repo=sql_alchemy_session_repository,
    )

    in_process_execution_trigger = Factory(
        InProcessExecutionTrigger,
        execute_agent_session=execute_agent_session,
    )

    on_task_ready = Factory(
        OnTaskReady,
    )
