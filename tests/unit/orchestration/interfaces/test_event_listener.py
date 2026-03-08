import pytest
from unittest.mock import AsyncMock, MagicMock
from agent_engine.orchestration.interfaces.event_listener import EventListenerRunner
from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
from agent_engine.shared.domain.value_objects.task_id import TaskId
import uuid

class TestEventListenerRunner:

    @pytest.fixture
    def listener(self):
        m = MagicMock()
        m.close = AsyncMock()
        return m


    @pytest.fixture
    def handle_task_ready(self):
        return AsyncMock()

    @pytest.fixture
    def runner(self, listener, handle_task_ready):
        return EventListenerRunner(
            listener=listener,
            handle_task_ready=handle_task_ready,
            project_id="target_project"
        )

    @pytest.mark.asyncio
    async def test_run_filters_project(self, runner, listener, handle_task_ready):
        # Setup listener to yield two events: one target, one ignored
        async def mock_listen():
            yield TaskReadyEvent(
                project_id="other_project",
                task_id=TaskId(value=uuid.uuid4()),
                planning_level="l1",
                status="ready",
                occurred_at="now"
            )
            yield TaskReadyEvent(
                project_id="target_project",
                task_id=TaskId(value=uuid.uuid4()),
                planning_level="l1",
                status="ready",
                occurred_at="now"
            )

        listener.listen.return_value = mock_listen()
        
        class MockResult:
            job_id = "job1"
            session_id = "sess1"
        handle_task_ready.execute.return_value = MockResult()

        await runner.run()

        # Should only have been called once for the target_project event
        handle_task_ready.execute.assert_called_once()
        listener.close.assert_called_once()
