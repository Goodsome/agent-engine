from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.orchestration.domain.value_objects.ready_task_dto import ReadyTaskDTO
from agent_engine.orchestration.application.use_cases.run_event_loop_tick import RunEventLoopTickResult
from agent_engine.orchestration.domain.value_objects.sop_content import SopContent
from agent_engine.orchestration.domain.ports.execution_trigger_port import TriggerSessionResult

class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    expected: Any

def _setup_mocks_success(task_query_port, job_repo, execution_trigger, sop_repo):
    task_query_port.fetch_ready_tasks.return_value = [
        ReadyTaskDTO(task_id=TaskId(value=uuid.uuid4()), planning_level="architecture", status="design", name="Task 1"),
        ReadyTaskDTO(task_id=TaskId(value=uuid.uuid4()), planning_level="implementation", status="develop", name="Task 2"),
    ]
    execution_trigger.trigger_session.return_value = TriggerSessionResult(
        session_id=SessionId(value=uuid.uuid4()),
        output=None,
        is_success=True,
    )
    sop_repo.get_sop.return_value = SopContent(system_prompt="You are a helpful agent", model_tier="pro")

TEST_CASES_EXECUTE: list[ExecuteCase] = [
    ExecuteCase(
        mocks_setup=_setup_mocks_success,
        expected=RunEventLoopTickResult(dispatched_count=2)
    )
]