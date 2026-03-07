from typing import Any, Callable, NamedTuple, TypedDict
from unittest.mock import patch, MagicMock

class RunCase(NamedTuple):
    mocks_setup: Callable
    system_prompt: str
    user_prompt: str
    tools: list[str]
    expected: Any

def _setup_mocks_success():
    patcher = patch('subprocess.run')
    mock_run_func = patcher.start()
    
    mock_result = MagicMock()
    mock_result.stdout = "Mocked Gemini Response\n"
    mock_run_func.return_value = mock_result

TEST_CASES_RUN: list[RunCase] = [
    RunCase(
        mocks_setup=_setup_mocks_success,
        system_prompt="system",
        user_prompt="user",
        tools=[],
        expected="Mocked Gemini Response"
    )
]