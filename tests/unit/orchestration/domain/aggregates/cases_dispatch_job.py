from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus

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

def _create_pending_job() -> DispatchJob:
    return DispatchJob(
        id=JobId(value=uuid.uuid4()),
        status=JobStatus.PENDING
    )

def _create_running_job() -> DispatchJob:
    job = _create_pending_job()
    job.status = JobStatus.RUNNING
    job.session_id = SessionId(value=uuid.uuid4())
    return job

dummy_session_id = SessionId(value=uuid.uuid4())

def _assert_mark_running(instance: DispatchJob) -> None:
    assert instance.status == JobStatus.RUNNING
    assert instance.session_id == dummy_session_id

def _assert_mark_completed(instance: DispatchJob) -> None:
    assert instance.status == JobStatus.COMPLETED

def _assert_mark_failed(instance: DispatchJob) -> None:
    assert instance.status == JobStatus.FAILED
    # Assuming reason isn't stored in DispatchJob attributes based on yaml, but let's just check status.
    # Actually wait, DispatchJob has mark_failed(reason: str), but doesn't have a 'reason' attribute in yaml.
    # So we just assert status is FAILED.

TEST_CASES_MARK_RUNNING: list[MarkRunningCase] = [
    MarkRunningCase(instance=_create_pending_job(), session_id=dummy_session_id, expected=_assert_mark_running)
]

TEST_CASES_MARK_COMPLETED: list[MarkCompletedCase] = [
    MarkCompletedCase(instance=_create_running_job(), expected=_assert_mark_completed)
]

TEST_CASES_MARK_FAILED: list[MarkFailedCase] = [
    MarkFailedCase(instance=_create_running_job(), reason="timeout", expected=_assert_mark_failed)
]
