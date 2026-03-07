from typing import Any, Callable, NamedTuple, TypedDict


class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    task_id: TaskId
    requirement: string
    session_type: SessionType
    expected: Any


TEST_CASES_EXECUTE: list[ExecuteCase] = []
