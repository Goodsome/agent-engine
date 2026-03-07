from typing import Any, Callable, NamedTuple, TypedDict

TEST_CASES_EXECUTE: list[ExecuteCase] = []


class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    expected: Any
