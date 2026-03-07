import pytest
from unittest.mock import MagicMock
from .cases_claude_agent_gateway import TEST_CASES_RUN


class TestClaudeAgentGateway:

    @pytest.fixture
    def claude_agent_gateway(self) -> None:
        from agent_engine.execution.infrastructure.claude_agent_gateway import (
            ClaudeAgentGateway,
        )

        return ClaudeAgentGateway()

    @pytest.mark.parametrize(
        "mocks_setup, system_prompt, user_prompt, tools, expected", TEST_CASES_RUN
    )
    def test_run(
        self,
        claude_agent_gateway,
        mocks_setup,
        system_prompt,
        user_prompt,
        tools,
        expected,
    ) -> None:
        mocks_setup()
        result = claude_agent_gateway.run(
            system_prompt=system_prompt, user_prompt=user_prompt, tools=tools
        )
        if callable(expected):
            expected(claude_agent_gateway)
        else:
            assert result == expected
