from typing import Any, Callable, NamedTuple, TypedDict
import uuid
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.orchestration.domain.aggregates.dispatch_job import DispatchJob
from agent_engine.orchestration.domain.enums import JobStatus

class SaveCase(NamedTuple):
    mocks_setup: Callable
    job: DispatchJob
    expected: Any

class DeleteCase(NamedTuple):
    mocks_setup: Callable
    dispatch_job_id: JobId
    expected: Any

class FindByIdCase(NamedTuple):
    mocks_setup: Callable
    dispatch_job_id: JobId
    expected: Any

def _setup_mocks_success():
    pass

job_id = JobId(value=uuid.uuid4())
dummy_job = DispatchJob(id=job_id, status=JobStatus.PENDING)

TEST_CASES_SAVE: list[SaveCase] = [
    SaveCase(mocks_setup=_setup_mocks_success, job=dummy_job, expected=None)
]
TEST_CASES_DELETE: list[DeleteCase] = [
    DeleteCase(mocks_setup=_setup_mocks_success, dispatch_job_id=job_id, expected=None)
]
TEST_CASES_FIND_BY_ID: list[FindByIdCase] = [
    FindByIdCase(mocks_setup=_setup_mocks_success, dispatch_job_id=job_id, expected=None)
]