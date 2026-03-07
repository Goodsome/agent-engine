from typing import Any, Callable, NamedTuple, TypedDict


class TriggerSessionCase(NamedTuple):
    mocks_setup: Callable
    job_id: JobId
    task_id: TaskId
    requirement: string
    expected: Any


TEST_CASES_TRIGGER_SESSION: list[TriggerSessionCase] = []
