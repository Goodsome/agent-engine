import pytest
from unittest.mock import AsyncMock, MagicMock
from .cases_handle_dispatchable_task_event import TEST_CASES_EXECUTE

class TestHandleDispatchableTaskEvent:

    @pytest.fixture
    def job_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def execution_trigger(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def sop_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, job_repo, execution_trigger, sop_repo) -> None:
        from agent_engine.orchestration.application.use_cases.handle_dispatchable_task_event import (
            HandleDispatchableTaskEvent,
        )

        return HandleDispatchableTaskEvent(
            job_repo=job_repo,
            execution_trigger=execution_trigger,
            sop_repo=sop_repo,
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("mocks_setup, event, expected", TEST_CASES_EXECUTE)
    async def test_execute(
        self,
        use_case,
        job_repo,
        execution_trigger,
        sop_repo,
        mocks_setup,
        event,
        expected,
    ) -> None:
        mocks_setup(job_repo, execution_trigger, sop_repo)
        result = await use_case.execute(event=event)
        expected(result)
        
        # Verify interactions
        assert job_repo.save.call_count == 2
        execution_trigger.trigger_session.assert_called_once()
        sop_repo.get_sop.assert_called_once_with(
            planning_level=event.planning_level, status=event.status
        )