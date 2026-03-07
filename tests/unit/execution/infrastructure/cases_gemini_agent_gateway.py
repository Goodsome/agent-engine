from typing import Any, Callable, NamedTuple, TypedDict
from unittest.mock import patch, AsyncMock

class RunCase(NamedTuple):
    mocks_setup: Callable
    system_prompt: str
    user_prompt: str
    tools: list[str]
    expected: Any

def _setup_mocks_success():
    patcher = patch('asyncio.create_subprocess_exec', new_callable=AsyncMock)
    mock_run_func = patcher.start()
    
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"Mocked Gemini Response\n", b"")
    mock_process.returncode = 0
    mock_run_func.return_value = mock_process

TEST_CASES_RUN: list[RunCase] = [
    RunCase(
        mocks_setup=_setup_mocks_success,
        system_prompt="system",
        user_prompt="user",
        tools=[],
        expected="Mocked Gemini Response"
    )
]