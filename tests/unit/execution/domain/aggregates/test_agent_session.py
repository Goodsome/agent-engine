import pytest
from .cases_agent_session import (
    TEST_CASES_FINISH_WITH_ERROR,
    TEST_CASES_FINISH_WITH_SUCCESS,
    TEST_CASES_START,
)


class TestAgentSession:

    @pytest.mark.parametrize("instance, expected", TEST_CASES_START)
    def test_start(self, instance, expected) -> None:
        actual = instance.start()
        if callable(expected):
            expected(instance)
        else:
            assert actual == expected

    @pytest.mark.parametrize(
        "instance, output, expected", TEST_CASES_FINISH_WITH_SUCCESS
    )
    def test_finish_with_success(self, instance, output, expected) -> None:
        actual = instance.finish_with_success(output=output)
        if callable(expected):
            expected(instance)
        else:
            assert actual == expected

    @pytest.mark.parametrize("instance, error, expected", TEST_CASES_FINISH_WITH_ERROR)
    def test_finish_with_error(self, instance, error, expected) -> None:
        actual = instance.finish_with_error(error=error)
        if callable(expected):
            expected(instance)
        else:
            assert actual == expected
