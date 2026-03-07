from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.execution.domain.aggregates.agent_session import AgentSession
from agent_engine.execution.domain.enums import SessionStatus
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.job_id import JobId

class StartCase(NamedTuple):
    instance: AgentSession
    expected: Any

class FinishWithSuccessCase(NamedTuple):
    instance: AgentSession
    output: str
    expected: Any

class FinishWithErrorCase(NamedTuple):
    instance: AgentSession
    error: str
    expected: Any

def _create_idle_session() -> AgentSession:
    return AgentSession(
        id=SessionId(value=uuid.uuid4()),
        job_id=JobId(value=uuid.uuid4()),
        context_payload={},
        status=SessionStatus.IDLE
    )

def _create_running_session() -> AgentSession:
    session = _create_idle_session()
    session.status = SessionStatus.RUNNING
    return session

def _assert_start(instance: AgentSession) -> None:
    assert instance.status == SessionStatus.RUNNING

def _assert_finish_success(instance: AgentSession) -> None:
    assert instance.status == SessionStatus.SUCCESS
    assert instance.final_output == "Done!"

def _assert_finish_error(instance: AgentSession) -> None:
    assert instance.status == SessionStatus.ERROR
    assert instance.error_message == "Failed!"

TEST_CASES_START: list[StartCase] = [
    StartCase(instance=_create_idle_session(), expected=_assert_start)
]

TEST_CASES_FINISH_WITH_SUCCESS: list[FinishWithSuccessCase] = [
    FinishWithSuccessCase(instance=_create_running_session(), output="Done!", expected=_assert_finish_success)
]

TEST_CASES_FINISH_WITH_ERROR: list[FinishWithErrorCase] = [
    FinishWithErrorCase(instance=_create_running_session(), error="Failed!", expected=_assert_finish_error)
]
