from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.execution.domain.aggregates.agent_session import AgentSession
from agent_engine.execution.domain.enums import SessionStatus

class SaveCase(NamedTuple):
    mocks_setup: Callable
    session: AgentSession
    expected: Any

class DeleteCase(NamedTuple):
    mocks_setup: Callable
    agent_session_id: SessionId
    expected: Any

class FindByIdCase(NamedTuple):
    mocks_setup: Callable
    agent_session_id: SessionId
    expected: Any

def _setup_mocks_success():
    pass

session_id = SessionId(value=uuid.uuid4())
dummy_session = AgentSession(
    id=session_id,
    job_id=JobId(value=uuid.uuid4()),
    context_payload={},
    status=SessionStatus.IDLE
)

TEST_CASES_SAVE: list[SaveCase] = [
    SaveCase(mocks_setup=_setup_mocks_success, session=dummy_session, expected=None)
]
TEST_CASES_DELETE: list[DeleteCase] = [
    DeleteCase(mocks_setup=_setup_mocks_success, agent_session_id=session_id, expected=None)
]
TEST_CASES_FIND_BY_ID: list[FindByIdCase] = [
    FindByIdCase(mocks_setup=_setup_mocks_success, agent_session_id=session_id, expected=None)
]