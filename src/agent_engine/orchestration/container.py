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
from agent_engine.orchestration.infrastructure.adapters.local_file_sop_repository import (
    LocalFileSopRepository,
)
from agent_engine.orchestration.infrastructure.adapters.pg_notify_event_listener import (
    PgNotifyEventListener,
)
from agent_engine.orchestration.application.use_cases.handle_task_ready_event import (
    HandleTaskReadyEvent,
)
from agent_engine.orchestration.interfaces.event_listener import EventListenerRunner


class Container(DeclarativeContainer):
    config = providers.Configuration()
    session_factory = providers.Dependency()
    execute_agent_session = providers.Dependency()

    task_graph_adapter = Factory(TaskGraphAdapter)
    sql_alchemy_dispatch_job_repository = Factory(
        SqlAlchemyDispatchJobRepository,
        session_factory=session_factory,
    )
    in_process_execution_trigger = Factory(
        InProcessExecutionTrigger,
        execute_agent_session=execute_agent_session,
    )
    local_file_sop_repository = Factory(LocalFileSopRepository)
    start_initial_workflow = Factory(
        StartInitialWorkflow,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
        sop_repo=local_file_sop_repository,
        project_id=config.PROJECT_ID,
    )
    run_event_loop_tick = Factory(
        RunEventLoopTick,
        task_query_port=task_graph_adapter,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
        sop_repo=local_file_sop_repository,
    )
    pg_notify_event_listener = Factory(
        PgNotifyEventListener,
        dsn=config.TASK_GRAPH_DATABASE_URL,
        channel=config.EVENT_BUS_CHANNEL,
    )
    handle_task_ready_event = Factory(
        HandleTaskReadyEvent,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
        sop_repo=local_file_sop_repository,
    )
    event_listener_runner = Factory(
        EventListenerRunner,
        listener=pg_notify_event_listener,
        handle_task_ready=handle_task_ready_event,
        project_id=config.PROJECT_ID,
    )
