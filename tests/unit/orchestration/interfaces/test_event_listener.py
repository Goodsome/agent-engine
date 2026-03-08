import pytest
from unittest.mock import AsyncMock, MagicMock
from agent_engine.orchestration.interfaces.event_listener import EventListenerRunner
from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
from agent_engine.orchestration.domain.events.task_review_requested_event import TaskReviewRequestedEvent
from agent_engine.shared.domain.value_objects.task_id import TaskId
from agent_engine.orchestration.domain.enums import PlanningLevel, TaskStatus
import uuid

class TestEventListenerRunner:

    @pytest.fixture
    def listener(self):
        m = MagicMock()
        m.close = AsyncMock()
        return m


    @pytest.fixture
    def handle_dispatchable_task(self):
        return AsyncMock()

    @pytest.fixture
    def runner(self, listener, handle_dispatchable_task):
        return EventListenerRunner(
            listener=listener,
            handle_dispatchable_task=handle_dispatchable_task,
            project_id="target_project"
        )

    @pytest.mark.asyncio
    async def test_run_filters_project(self, runner, listener, handle_dispatchable_task):
        # Setup listener to yield events: one ignored, two target (Ready & Review)
        async def mock_listen():
            yield TaskReadyEvent(
                project_id="other_project",
                task_id=TaskId(value=uuid.uuid4()),
                planning_level=PlanningLevel.ATOMIC
            )
            yield TaskReadyEvent(
                project_id="target_project",
                task_id=TaskId(value=uuid.uuid4()),
                planning_level=PlanningLevel.ATOMIC
            )
            yield TaskReviewRequestedEvent(
                project_id="target_project",
                task_id=TaskId(value=uuid.uuid4()),
                planning_level=PlanningLevel.FEATURE
            )

        listener.listen.return_value = mock_listen()
        
        class MockResult:
            job_id = "job1"
            session_id = "sess1"
        handle_dispatchable_task.execute.return_value = MockResult()

        await runner.run()

        # Should have been called twice for the target_project events
        assert handle_dispatchable_task.execute.call_count == 2
        listener.close.assert_called_once()