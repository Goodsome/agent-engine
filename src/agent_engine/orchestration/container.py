from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Configuration, Dependency
from agent_engine.orchestration.infrastructure.repositories.sql_alchemy_session_repository import (
    SqlAlchemySessionRepository,
)
from agent_engine.orchestration.application.use_cases.dispatch_task import DispatchTask
from agent_engine.orchestration.application.use_cases.review_task import ReviewTask
from agent_engine.orchestration.application.use_cases.revise_task import ReviseTask
from agent_engine.orchestration.application.event_handlers.on_task_ready import OnTaskReady
from agent_engine.orchestration.application.event_handlers.on_task_review_requested import OnTaskReviewRequested
from agent_engine.orchestration.application.event_handlers.on_task_changes_requested import OnTaskChangesRequested


class Container(DeclarativeContainer):
    config: Configuration = Configuration()
    session_factory = Dependency()
    
    # 外部依赖
    execute_session = Dependency()
    agent_profile_query_service = Dependency()
    
    sql_alchemy_session_repository: Factory[SqlAlchemySessionRepository] = Factory(
        SqlAlchemySessionRepository,
        session_factory=session_factory,
    )

    dispatch_task: Factory[DispatchTask] = Factory(
        DispatchTask,
        agent_profile_query_service=agent_profile_query_service,
        execute_session_use_case=execute_session,
        session_repository=sql_alchemy_session_repository,
    )
    
    review_task: Factory[ReviewTask] = Factory(
        ReviewTask,
        session_repository=sql_alchemy_session_repository,
        execute_session_use_case=execute_session,
    )

    on_task_ready: Factory[OnTaskReady] = Factory(
        OnTaskReady,
        dispatch_task_use_case=dispatch_task,
    )

    on_task_review_requested: Factory[OnTaskReviewRequested] = Factory(
        OnTaskReviewRequested,
        review_task_use_case=review_task,
    )

    revise_task: Factory[ReviseTask] = Factory(
        ReviseTask,
        session_repository=sql_alchemy_session_repository,
        execute_session_use_case=execute_session,
    )

    on_task_changes_requested: Factory[OnTaskChangesRequested] = Factory(
        OnTaskChangesRequested,
        revise_task_use_case=revise_task,
    )
