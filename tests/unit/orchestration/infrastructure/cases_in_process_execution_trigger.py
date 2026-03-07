from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.execution.application.use_cases.execute_agent_session import ExecuteAgentSessionResult

class TriggerSessionCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    system_prompt: str
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
        mocks_setup=lambda: None,
        job_id=JobId(value=uuid.UUID("22222222-2222-2222-2222-222222222222")),
        system_prompt="You are a helpful planner",
        requirement="Hello",
        expected=SessionId(value=uuid.UUID("33333333-3333-3333-3333-333333333333"))
    )
]