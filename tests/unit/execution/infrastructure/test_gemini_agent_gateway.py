import pytest
from unittest.mock import MagicMock
from .cases_gemini_agent_gateway import TEST_CASES_RUN


class TestGeminiAgentGateway:

    @pytest.fixture
    def gemini_agent_gateway(self) -> None:
        from agent_engine.execution.infrastructure.gemini_agent_gateway import (
            GeminiAgentGateway,
        )

        return GeminiAgentGateway()

    @pytest.mark.parametrize(
        "mocks_setup, system_prompt, user_prompt, tools, expected", TEST_CASES_RUN
    )
    def test_run(
        self,
        gemini_agent_gateway,
        mocks_setup,
        system_prompt,
        user_prompt,
        tools,
        expected,
    ) -> None:
        mocks_setup()
        result = gemini_agent_gateway.run(
            system_prompt=system_prompt, user_prompt=user_prompt, tools=tools
        )
        if callable(expected):
            expected(gemini_agent_gateway)
        else:
            assert result == expected
