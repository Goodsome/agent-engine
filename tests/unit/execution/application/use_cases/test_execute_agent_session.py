import pytest
from unittest.mock import AsyncMock, MagicMock
from .cases_execute_agent_session import TEST_CASES_EXECUTE


class TestExecuteAgentSession:

    @pytest.fixture
    def agent_gateway(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def session_repo(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, agent_gateway, session_repo) -> None:
        from agent_engine.execution.application.use_cases.execute_agent_session import (
            ExecuteAgentSession,
        )

        return ExecuteAgentSession(
            agent_gateway=agent_gateway, session_repo=session_repo
        )

    @pytest.mark.parametrize(
        "mocks_setup, job_id, system_prompt, requirement, expected",
        TEST_CASES_EXECUTE,
    )
    async def test_execute(
        self,
        use_case,
        agent_gateway,
        session_repo,
        mocks_setup,
        job_id,
        system_prompt,
        requirement,
        expected,
    ) -> None:
        from agent_engine.execution.application.use_cases.execute_agent_session import ExecuteAgentSessionCommand
        mocks_setup(agent_gateway, session_repo)
        cmd = ExecuteAgentSessionCommand(
            job_id=job_id,
            system_prompt=system_prompt,
            requirement=requirement,
        )
        result = await use_case.execute(cmd=cmd)
        if callable(expected):
            assert expected(result)
        else:
            assert result == expected
