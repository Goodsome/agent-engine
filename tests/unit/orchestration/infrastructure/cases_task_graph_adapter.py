from typing import Any, Callable, NamedTuple, TypedDict


class FetchReadyTasksCase(NamedTuple):
    mocks_setup: Callable
    expected: Any


TEST_CASES_FETCH_READY_TASKS: list[FetchReadyTasksCase] = []
