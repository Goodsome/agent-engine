from typing import Any, Callable, NamedTuple, TypedDict

class RunCase(NamedTuple):
    mocks_setup: Callable
    system_prompt: str
    user_prompt: str
    tools: list[str]
    expected: Any

def _setup_mocks_success():
    pass

TEST_CASES_RUN: list[RunCase] = [
    RunCase(
        mocks_setup=_setup_mocks_success,
        system_prompt="system",
        user_prompt="user",
        tools=[],
        expected="Mocked Gemini Response"
    )
]