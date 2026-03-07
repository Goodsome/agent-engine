from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.execution.application.use_cases.execute_agent_session import ExecuteAgentSessionResult

class TriggerSessionCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    task_id: TaskId | None
    requirement: str
    expected: Any

def _setup_mocks_success(trigger_instance):
    mock_result = ExecuteAgentSessionResult(
        session_id=SessionId(value=uuid.UUID("33333333-3333-3333-3333-333333333333")),
        is_success=True
    )
    trigger_instance.execute_agent_session.execute.return_value = mock_result

TEST_CASES_TRIGGER_SESSION: list[TriggerSessionCase] = [
    TriggerSessionCase(
        mocks_setup=lambda: None,  # We'll set it up via the callable `expected` check or a mock injection hook
        job_id=JobId(value=uuid.UUID("22222222-2222-2222-2222-222222222222")),
        task_id=None,
        requirement="Hello",
        expected=SessionId(value=uuid.UUID("33333333-3333-3333-3333-333333333333"))
    )
]