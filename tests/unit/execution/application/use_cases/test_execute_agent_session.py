import pytest
from unittest.mock import AsyncMock, MagicMock
from .cases_execute_agent_session import TEST_CASES_EXECUTE


class TestExecuteAgentSession:

    @pytest.fixture
    def agent_gateway(self) -> None:
        return MagicMock()

    @pytest.fixture
    def sop_repo(self) -> None:
        return MagicMock()

    @pytest.fixture
    def session_repo(self) -> None:
        return MagicMock()

    @pytest.fixture
    def use_case(self, agent_gateway, sop_repo, session_repo) -> None:
        from agent_engine.execution.application.use_cases.execute_agent_session import (
            ExecuteAgentSession,
        )

        return ExecuteAgentSession(
            agent_gateway=agent_gateway, sop_repo=sop_repo, session_repo=session_repo
        )

    @pytest.mark.parametrize(
        "mocks_setup, job_id, task_id, requirement, session_type, expected",
        TEST_CASES_EXECUTE,
    )
    def test_execute(
        self,
        use_case,
        agent_gateway,
        sop_repo,
        session_repo,
        mocks_setup,
        job_id,
        task_id,
        requirement,
        session_type,
        expected,
    ) -> None:
        mocks_setup(agent_gateway, sop_repo, session_repo)
        result = use_case.execute(
            job_id=job_id,
            task_id=task_id,
            requirement=requirement,
            session_type=session_type,
        )
        assert result == expected
