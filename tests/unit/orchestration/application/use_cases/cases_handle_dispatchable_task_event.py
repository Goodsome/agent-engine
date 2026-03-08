from typing import Any, Callable, NamedTuple, Union
import uuid
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
from agent_engine.orchestration.domain.events.task_review_requested_event import TaskReviewRequestedEvent
from agent_engine.orchestration.application.use_cases.handle_dispatchable_task_event import HandleDispatchableTaskEventResult
from agent_engine.orchestration.domain.enums import PlanningLevel, TaskStatus

class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    event: Union[TaskReadyEvent, TaskReviewRequestedEvent]
    expected: Any

def _setup_mocks_success(job_repo, execution_trigger, sop_repo):
    execution_trigger.trigger_session.return_value = SessionId(value=uuid.UUID("12345678-1234-5678-1234-567812345678"))
    sop_repo.get_sop.return_value = "You are a helpful agent"
    # mock save to just return
    job_repo.save.return_value = None

def _assert_success(result: HandleDispatchableTaskEventResult):
    assert result.session_id == "12345678-1234-5678-1234-567812345678"
    assert isinstance(result.job_id, str)

TEST_CASES_EXECUTE: list[ExecuteCase] = [
    ExecuteCase(
        mocks_setup=_setup_mocks_success,
        event=TaskReadyEvent(
            project_id="test_project",
            task_id=TaskId(value=uuid.UUID("87654321-4321-8765-4321-876543210987")),
            planning_level=PlanningLevel.ARCHITECTURAL,
            status=TaskStatus.READY
        ),
        expected=_assert_success
    ),
    ExecuteCase(
        mocks_setup=_setup_mocks_success,
        event=TaskReviewRequestedEvent(
            project_id="test_project",
            task_id=TaskId(value=uuid.UUID("87654321-4321-8765-4321-876543210987")),
            planning_level=PlanningLevel.FEATURE,
            status=TaskStatus.REVIEW
        ),
        expected=_assert_success
    )
]
