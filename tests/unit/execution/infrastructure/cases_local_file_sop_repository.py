from typing import Any, Callable, NamedTuple, TypedDict


class GetSopCase(NamedTuple):
    mocks_setup: Callable
    session_type: SessionType
    expected: Any


class SaveCase(NamedTuple):
    mocks_setup: Callable
    sop: Sop
    expected: Any


class DeleteCase(NamedTuple):
    mocks_setup: Callable
    sop_id: UUID
    expected: Any


class FindByIdCase(NamedTuple):
    mocks_setup: Callable
    sop_id: UUID
    expected: Any


TEST_CASES_GET_SOP: list[GetSopCase] = []
TEST_CASES_SAVE: list[SaveCase] = []
TEST_CASES_DELETE: list[DeleteCase] = []
TEST_CASES_FIND_BY_ID: list[FindByIdCase] = []
