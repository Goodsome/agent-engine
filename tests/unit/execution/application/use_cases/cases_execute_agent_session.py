from typing import Any, Callable, NamedTuple, TypedDict

TEST_CASES_EXECUTE: list[ExecuteCase] = []


class ExecuteCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    task_id: TaskId
    requirement: str
    session_type: SessionType
    expected: Any
