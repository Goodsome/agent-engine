import json
import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agent_engine.orchestration.infrastructure.adapters.pg_notify_event_listener import PgNotifyEventListener
from agent_engine.orchestration.domain.enums import PlanningLevel, TaskStatus

class TestPgNotifyEventListener:
    @pytest.fixture
    def mock_conn(self):
        conn = MagicMock()
        conn.execute = AsyncMock()
        conn.close = AsyncMock()
        return conn

    @pytest.fixture
    def listener(self):
        return PgNotifyEventListener(dsn="postgresql://user:pass@localhost:5432/db", channel="test_channel")

    @patch("psycopg.AsyncConnection.connect", new_callable=AsyncMock)
    async def test_listen(self, mock_connect, listener, mock_conn):
        mock_connect.return_value = mock_conn
        
        # Mock notifies generator
        class MockNotify:
            def __init__(self, payload):
                self.payload = payload
                
        async def mock_notifies():
            valid_payload_ready = {
                "event_type": "TaskReadyEvent",
                "project_id": "proj_1",
                "task_id": {"value": "12345678-1234-5678-1234-567812345678"},
                "planning_level": PlanningLevel.ATOMIC.value,
                "status": TaskStatus.READY.value,
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
            valid_payload_review = {
                "event_type": "TaskReviewRequestedEvent",
                "project_id": "proj_1",
                "task_id": {"value": "87654321-4321-8765-4321-876543210987"},
                "planning_level": PlanningLevel.FEATURE.value,
                "status": TaskStatus.REVIEW.value,
                "occurred_at": datetime.now(timezone.utc).isoformat()
            }
            # Add an invalid payload to test try-except
            yield MockNotify("invalid json")
            yield MockNotify(json.dumps({"event_type": "UnknownEvent"}))
            yield MockNotify(json.dumps(valid_payload_ready))
            yield MockNotify(json.dumps(valid_payload_review))
            
        mock_conn.notifies.return_value = mock_notifies()
        
        events = []
        async for event in listener.listen():
            events.append(event)
            
        assert len(events) == 2
        assert events[0].project_id == "proj_1"
        assert events[0].event_type == "TaskReadyEvent"
        assert events[1].project_id == "proj_1"
        assert events[1].event_type == "TaskReviewRequestedEvent"
        
        mock_connect.assert_called_once()
        mock_conn.execute.assert_called_once_with("LISTEN test_channel")

    @patch("psycopg.AsyncConnection.connect", new_callable=AsyncMock)
    async def test_close(self, mock_connect, listener, mock_conn):
        mock_connect.return_value = mock_conn
        
        # Call listen to establish connection
        async def mock_notifies():
            return
            yield # make it a generator
        mock_conn.notifies.return_value = mock_notifies()
        
        # establish connection
        it = listener.listen()
        try:
            await it.__anext__()
        except StopAsyncIteration:
            pass
            
        # mock closed property
        mock_conn.closed = False
        
        await listener.close()
        mock_conn.close.assert_called_once()
