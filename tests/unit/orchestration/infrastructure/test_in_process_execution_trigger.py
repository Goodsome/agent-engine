import pytest
from unittest.mock import MagicMock
from .cases_in_process_execution_trigger import TEST_CASES_TRIGGER_SESSION


class TestInProcessExecutionTrigger:

    @pytest.fixture
    def in_process_execution_trigger(self) -> None:
        from agent_engine.orchestration.infrastructure.in_process_execution_trigger import (
            InProcessExecutionTrigger,
        )

        return InProcessExecutionTrigger()

    @pytest.mark.parametrize(
        "mocks_setup, job_id, task_id, requirement, expected",
        TEST_CASES_TRIGGER_SESSION,
    )
    def test_trigger_session(
        self,
        in_process_execution_trigger,
        mocks_setup,
        job_id,
        task_id,
        requirement,
        expected,
    ) -> None:
        mocks_setup()
        result = in_process_execution_trigger.trigger_session(
            job_id=job_id, task_id=task_id, requirement=requirement
        )
        if callable(expected):
            expected(in_process_execution_trigger)
        else:
            assert result == expected
