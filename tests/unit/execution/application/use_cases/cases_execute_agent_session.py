from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.execution.domain.enums import SessionType
from agent_engine.execution.application.use_cases.execute_agent_session import ExecuteAgentSessionResult

class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    task_id: TaskId | None
    requirement: str
    session_type: SessionType
    expected: Any

def _setup_mocks_success(agent_gateway, sop_repo, session_repo):
    sop_repo.get_sop.return_value = "You are a helpful planner"
    agent_gateway.run.return_value = "Plan created successfully"

TEST_CASES_EXECUTE: list[ExecuteCase] = [
    ExecuteCase(
        mocks_setup=_setup_mocks_success,
        job_id=JobId(value=uuid.UUID("22222222-2222-2222-2222-222222222222")),
        task_id=None,
        requirement="Do something",
        session_type=SessionType.PLANNER,
        # session_id is auto-generated inside, so we'll assert using a custom callback or relax the check
        # For simplicity, we can provide a callable to assert the result's properties
        expected=lambda result: getattr(result, "is_success") is True and result.output == "Plan created successfully"
    )
]