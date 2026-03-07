import pytest
from unittest.mock import AsyncMock, MagicMock
from .cases_run_event_loop_tick import TEST_CASES_EXECUTE


class TestRunEventLoopTick:

    @pytest.fixture
    def task_query_port(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def job_repo(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def execution_trigger(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, task_query_port, job_repo, execution_trigger) -> None:
        from agent_engine.orchestration.application.use_cases.run_event_loop_tick import (
            RunEventLoopTick,
        )

        return RunEventLoopTick(
            task_query_port=task_query_port,
            job_repo=job_repo,
            execution_trigger=execution_trigger,
        )

    @pytest.mark.parametrize("mocks_setup, expected", TEST_CASES_EXECUTE)
    async def test_execute(
        self,
        use_case,
        task_query_port,
        job_repo,
        execution_trigger,
        mocks_setup,
        expected,
    ) -> None:
        from agent_engine.orchestration.application.use_cases.run_event_loop_tick import RunEventLoopTickCommand
        mocks_setup(task_query_port, job_repo, execution_trigger)
        result = await use_case.execute(cmd=RunEventLoopTickCommand())
        assert result == expected
