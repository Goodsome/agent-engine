from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.execution.application.use_cases.execute_agent_session import ExecuteAgentSessionResult

class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    system_prompt: str
    requirement: str
    expected: Any

def _setup_mocks_success(agent_gateway, session_repo):
    agent_gateway.run.return_value = "Plan created successfully"

TEST_CASES_EXECUTE: list[ExecuteCase] = [
    ExecuteCase(
        mocks_setup=_setup_mocks_success,
        job_id=JobId(value=uuid.UUID("22222222-2222-2222-2222-222222222222")),
        system_prompt="You are a helpful planner",
        requirement="Do something",
        expected=lambda result: getattr(result, "is_success") is True and result.output == "Plan created successfully"
    )
]