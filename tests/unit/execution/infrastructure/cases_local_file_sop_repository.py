from typing import Any, Callable, NamedTuple, TypedDict
from agent_engine.execution.domain.enums import SessionType

class GetSopCase(NamedTuple):
    mocks_setup: Callable
    session_type: SessionType
    expected: Any

def _setup_mocks_success():
    pass

TEST_CASES_GET_SOP: list[GetSopCase] = [
    GetSopCase(
        mocks_setup=_setup_mocks_success,
        session_type=SessionType.PLANNER,
        expected="You are a planner."
    )
]

# The following were auto-generated but are not defined in codegen.yaml for SopRepository
TEST_CASES_SAVE: list[Any] = []
TEST_CASES_DELETE: list[Any] = []
TEST_CASES_FIND_BY_ID: list[Any] = []