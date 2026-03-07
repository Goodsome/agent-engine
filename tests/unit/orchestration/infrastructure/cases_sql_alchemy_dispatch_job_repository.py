from typing import Any, Callable, NamedTuple, TypedDict


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


TEST_CASES_SAVE: list[SaveCase] = []
TEST_CASES_DELETE: list[DeleteCase] = []
TEST_CASES_FIND_BY_ID: list[FindByIdCase] = []
