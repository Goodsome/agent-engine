from typing import Any, Callable, NamedTuple, TypedDict

TEST_CASES_RUN: list[RunCase] = []


class RunCase(NamedTuple):
    mocks_setup: Callable
    system_prompt: str
    user_prompt: str
    tools: str
    expected: Any
