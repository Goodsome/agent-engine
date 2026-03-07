from agent_engine.orchestration.application.use_cases.run_event_loop_tick import (
    RunEventLoopTick,
)
from agent_engine.orchestration.infrastructure.clients.task_graph_adapter import (
    TaskGraphAdapter,
)
from agent_engine.orchestration.application.use_cases.start_initial_workflow import (
    StartInitialWorkflow,
)
from agent_engine.orchestration.infrastructure.repositories.sql_alchemy_dispatch_job_repository import (
    SqlAlchemyDispatchJobRepository,
)
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory
from agent_engine.orchestration.infrastructure.clients.in_process_execution_trigger import (
    InProcessExecutionTrigger,
)


class Container(DeclarativeContainer):
    task_graph_adapter = Factory(TaskGraphAdapter)
    sql_alchemy_dispatch_job_repository = Factory(SqlAlchemyDispatchJobRepository)
    in_process_execution_trigger = Factory(InProcessExecutionTrigger)
    start_initial_workflow = Factory(
        StartInitialWorkflow,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
    )
    run_event_loop_tick = Factory(
        RunEventLoopTick,
        task_query_port=task_graph_adapter,
        job_repo=sql_alchemy_dispatch_job_repository,
        execution_trigger=in_process_execution_trigger,
    )
