import pytest
from unittest.mock import MagicMock, AsyncMock
from .cases_in_process_execution_trigger import TEST_CASES_TRIGGER_SESSION


class TestInProcessExecutionTrigger:

    @pytest.fixture
    def execute_agent_session_mock(self):
        return AsyncMock()

    @pytest.fixture
    def in_process_execution_trigger(self, execute_agent_session_mock) -> None:
        from agent_engine.orchestration.infrastructure.adapters.in_process_execution_trigger import (
            InProcessExecutionTrigger,
        )

        return InProcessExecutionTrigger(execute_agent_session=execute_agent_session_mock)

    @pytest.mark.parametrize(
        "mocks_setup, job_id, system_prompt, requirement, expected",
        TEST_CASES_TRIGGER_SESSION,
    )
    async def test_trigger_session(
        self,
        in_process_execution_trigger,
        mocks_setup,
        job_id,
        system_prompt,
        requirement,
        expected,
    ) -> None:
        from agent_engine.shared.domain.value_objects.session_id import SessionId
        import uuid
        from agent_engine.execution.application.use_cases.execute_agent_session import ExecuteAgentSessionResult

        in_process_execution_trigger.execute_agent_session.execute.return_value = ExecuteAgentSessionResult(
            session_id=SessionId(value=uuid.UUID("33333333-3333-3333-3333-333333333333")),
            is_success=True
        )

        result = await in_process_execution_trigger.trigger_session(
            job_id=job_id, system_prompt=system_prompt, requirement=requirement
        )
        if callable(expected):
            assert expected(result)
        else:
            assert result == expected
