import pytest
from unittest.mock import AsyncMock, MagicMock
from .cases_start_initial_workflow import TEST_CASES_EXECUTE


class TestStartInitialWorkflow:

    @pytest.fixture
    def job_repo(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def execution_trigger(self) -> None:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, job_repo, execution_trigger) -> None:
        from agent_engine.orchestration.application.use_cases.start_initial_workflow import (
            StartInitialWorkflow,
        )

        return StartInitialWorkflow(
            job_repo=job_repo, execution_trigger=execution_trigger
        )

    @pytest.mark.parametrize(
        "mocks_setup, raw_requirement, expected", TEST_CASES_EXECUTE
    )
    async def test_execute(
        self,
        use_case,
        job_repo,
        execution_trigger,
        mocks_setup,
        raw_requirement,
        expected,
    ) -> None:
        from agent_engine.orchestration.application.use_cases.start_initial_workflow import StartInitialWorkflowCommand
        mocks_setup(job_repo, execution_trigger)
        result = await use_case.execute(cmd=StartInitialWorkflowCommand(raw_requirement=raw_requirement))
        assert result == expected
