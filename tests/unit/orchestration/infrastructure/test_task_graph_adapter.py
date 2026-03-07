import pytest
from unittest.mock import MagicMock
from .cases_task_graph_adapter import TEST_CASES_FETCH_READY_TASKS


class TestTaskGraphAdapter:

    @pytest.fixture
    def task_graph_adapter(self) -> None:
        from agent_engine.orchestration.infrastructure.task_graph_adapter import (
            TaskGraphAdapter,
        )

        return TaskGraphAdapter()

    @pytest.mark.parametrize("mocks_setup, expected", TEST_CASES_FETCH_READY_TASKS)
    def test_fetch_ready_tasks(self, task_graph_adapter, mocks_setup, expected) -> None:
        mocks_setup()
        result = task_graph_adapter.fetch_ready_tasks()
        if callable(expected):
            expected(task_graph_adapter)
        else:
            assert result == expected
