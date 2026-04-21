from agent_engine.orchestration.application.use_cases.run_event_loop_tick import (
    RunEventLoopTick,
)
from agent_engine.orchestration.infrastructure.adapters.task_graph_adapter import (
    TaskGraphAdapter,
)
from agent_engine.orchestration.application.use_cases.start_initial_workflow import (
    StartInitialWorkflow,
)
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
from agent_engine.orchestration.infrastructure.adapters.pg_notify_event_listener import (
    PgNotifyEventListener,
)
from agent_engine.orchestration.application.use_cases.handle_dispatchable_task_event import (
    HandleDispatchableTaskEvent,
)
from agent_engine.orchestration.interfaces.event_listener import EventListenerRunner


class Container(DeclarativeContainer):
    config = providers.Configuration()
    session_factory = providers.Dependency()
    
    # 外部依赖
    handle_dispatch_command = providers.Dependency()
    blueprint_registry = providers.Dependency()

    task_graph_adapter = Factory(TaskGraphAdapter)
    
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
        dispatch_handler=handle_dispatch_command,
        session_repo=sql_alchemy_session_repository,
    )

    in_process_execution_trigger = Factory(
        InProcessExecutionTrigger,
        execute_agent_session=execute_agent_session,
    )

    start_initial_workflow = Factory(
        StartInitialWorkflow,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
        blueprint_registry=blueprint_registry,
        project_id=config.PROJECT_ID,
    )
    run_event_loop_tick = Factory(
        RunEventLoopTick,
        task_query_port=task_graph_adapter,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
        blueprint_registry=blueprint_registry,
    )
    pg_notify_event_listener = Factory(
        PgNotifyEventListener,
        dsn=config.TASK_GRAPH_DATABASE_URL,
        channel=config.EVENT_BUS_CHANNEL,
    )
    handle_dispatchable_task_event = Factory(
        HandleDispatchableTaskEvent,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
        blueprint_registry=blueprint_registry,
    )
    event_listener_runner = Factory(
        EventListenerRunner,
        listener=pg_notify_event_listener,
        handle_dispatchable_task=handle_dispatchable_task_event,
        project_id=config.PROJECT_ID,
    )
