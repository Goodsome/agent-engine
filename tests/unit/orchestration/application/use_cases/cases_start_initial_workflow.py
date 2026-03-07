from typing import Any, Callable, NamedTuple, TypedDict


class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    raw_requirement: string
    expected: Any


TEST_CASES_EXECUTE: list[ExecuteCase] = []
