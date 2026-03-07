from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.orchestration.domain.value_objects.ready_task_dto import ReadyTaskDTO
from agent_engine.orchestration.application.use_cases.run_event_loop_tick import RunEventLoopTickResult

class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    expected: Any

def _setup_mocks_success(task_query_port, job_repo, execution_trigger):
    task_query_port.fetch_ready_tasks.return_value = [
        ReadyTaskDTO(task_id=TaskId(value=uuid.uuid4()), planning_level="High", name="Task 1"),
        ReadyTaskDTO(task_id=TaskId(value=uuid.uuid4()), planning_level="Medium", name="Task 2"),
    ]
    execution_trigger.trigger_session.return_value = SessionId(value=uuid.uuid4())

TEST_CASES_EXECUTE: list[ExecuteCase] = [
    ExecuteCase(
        mocks_setup=_setup_mocks_success,
        expected=RunEventLoopTickResult(dispatched_count=2)
    )
]