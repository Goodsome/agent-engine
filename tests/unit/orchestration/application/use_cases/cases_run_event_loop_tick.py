from typing import Any, Callable, NamedTuple, TypedDict


class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    expected: Any


TEST_CASES_EXECUTE: list[ExecuteCase] = []
