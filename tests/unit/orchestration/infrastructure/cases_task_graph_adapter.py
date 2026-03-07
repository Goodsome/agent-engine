from typing import Any, Callable, NamedTuple, TypedDict

class FetchReadyTasksCase(NamedTuple):
    mocks_setup: Callable
    expected: Any

def _setup_mocks_success():
    pass

TEST_CASES_FETCH_READY_TASKS: list[FetchReadyTasksCase] = [
    FetchReadyTasksCase(
        mocks_setup=_setup_mocks_success,
        expected=[]
    )
]