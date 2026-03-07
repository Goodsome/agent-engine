from typing import Any, Callable, NamedTuple, TypedDict
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob

TEST_CASES_MARK_RUNNING: list[MarkRunningCase] = []
TEST_CASES_MARK_COMPLETED: list[MarkCompletedCase] = []
TEST_CASES_MARK_FAILED: list[MarkFailedCase] = []


class MarkRunningCase(NamedTuple):
    instance: DispatchJob
    session_id: SessionId
    expected: Any


class MarkCompletedCase(NamedTuple):
    instance: DispatchJob
    expected: Any


class MarkFailedCase(NamedTuple):
    instance: DispatchJob
    reason: str
    expected: Any
