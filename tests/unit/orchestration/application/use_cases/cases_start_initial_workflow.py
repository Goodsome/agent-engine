from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.orchestration.application.use_cases.start_initial_workflow import StartInitialWorkflowResult

class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    raw_requirement: str
    expected: Any

def _setup_mocks_success(job_repo, execution_trigger):
    mock_session_id = SessionId(value=uuid.UUID("11111111-1111-1111-1111-111111111111"))
    execution_trigger.trigger_session.return_value = mock_session_id

TEST_CASES_EXECUTE: list[ExecuteCase] = [
    ExecuteCase(
        mocks_setup=_setup_mocks_success,
        raw_requirement="Help me build a web app",
        expected=StartInitialWorkflowResult(initial_session_id="11111111-1111-1111-1111-111111111111")
    )
]