from typing import Any, Callable, NamedTuple, TypedDict


class RunCase(NamedTuple):
    mocks_setup: Callable
    system_prompt: string
    user_prompt: string
    tools: string
    expected: Any


TEST_CASES_RUN: list[RunCase] = []
