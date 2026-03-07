from typing import Any, Callable, NamedTuple, TypedDict
from unittest.mock import patch

class RunCase(NamedTuple):
    mocks_setup: Callable
    system_prompt: str
    user_prompt: str
    tools: list[str]
    expected: Any

def _setup_mocks_success():
    from claude_agent_sdk import AssistantMessage
    
    class MockBlock:
        def __init__(self, text):
            self.text = text
            
    # Subclass to bypass complex pydantic instantiation if any, but let's try direct instantiation first.
    class MockMessage:
        def __init__(self):
            self.content = [MockBlock("Mocked Claude Response")]
            
    # We must patch the isinstance check for it to match AssistantMessage
    # OR we can just patch `query` to yield a real AssistantMessage.
    # Let's try subclassing or using Mock.
    # Actually, we can patch `claude_agent_gateway.query` to return an async generator
    async def mock_query(*args, **kwargs):
        # We can just create an object that has __class__ as AssistantMessage
        # Actually in python you can assign __class__ for MagicMock
        msg = MockMessage()
        msg.__class__ = AssistantMessage
        yield msg

    patcher = patch('agent_engine.execution.infrastructure.adapters.claude_agent_gateway.query', new=mock_query)
    patcher.start()

TEST_CASES_RUN: list[RunCase] = [
    RunCase(
        mocks_setup=_setup_mocks_success,
        system_prompt="system",
        user_prompt="user",
        tools=[],
        expected="Mocked Claude Response"
    )
]