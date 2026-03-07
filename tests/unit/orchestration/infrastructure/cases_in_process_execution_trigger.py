from typing import Any, Callable, NamedTuple, TypedDict

TEST_CASES_TRIGGER_SESSION: list[TriggerSessionCase] = []


class TriggerSessionCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    task_id: TaskId
    requirement: str
    expected: Any
