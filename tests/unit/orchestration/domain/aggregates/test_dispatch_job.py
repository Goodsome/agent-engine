import pytest
from .cases_dispatch_job import (
    TEST_CASES_MARK_COMPLETED,
    TEST_CASES_MARK_FAILED,
    TEST_CASES_MARK_RUNNING,
)


class TestDispatchJob:

    @pytest.mark.parametrize("instance, session_id, expected", TEST_CASES_MARK_RUNNING)
    def test_mark_running(self, instance, session_id, expected) -> None:
        actual = instance.mark_running(session_id=session_id)
        if callable(expected):
            expected(instance)
        else:
            assert actual == expected

    @pytest.mark.parametrize("instance, expected", TEST_CASES_MARK_COMPLETED)
    def test_mark_completed(self, instance, expected) -> None:
        actual = instance.mark_completed()
        if callable(expected):
            expected(instance)
        else:
            assert actual == expected

    @pytest.mark.parametrize("instance, reason, expected", TEST_CASES_MARK_FAILED)
    def test_mark_failed(self, instance, reason, expected) -> None:
        actual = instance.mark_failed(reason=reason)
        if callable(expected):
            expected(instance)
        else:
            assert actual == expected
