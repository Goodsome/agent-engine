from typing import Any, Callable, NamedTuple, TypedDict

TEST_CASES_FETCH_READY_TASKS: list[FetchReadyTasksCase] = []


class FetchReadyTasksCase(NamedTuple):
    mocks_setup: Callable
    expected: Any
