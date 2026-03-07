from typing import Any, Callable, NamedTuple, TypedDict

TEST_CASES_GET_SOP: list[GetSopCase] = []


class GetSopCase(NamedTuple):
    mocks_setup: Callable
    session_type: SessionType
    expected: Any
