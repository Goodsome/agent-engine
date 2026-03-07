import pytest
from unittest.mock import MagicMock
from .cases_local_file_sop_repository import TEST_CASES_GET_SOP


class TestLocalFileSopRepository:

    @pytest.fixture
    def local_file_sop_repository(self) -> None:
        from agent_engine.execution.infrastructure.local_file_sop_repository import (
            LocalFileSopRepository,
        )

        return LocalFileSopRepository()

    @pytest.mark.parametrize("mocks_setup, session_type, expected", TEST_CASES_GET_SOP)
    def test_get_sop(
        self, local_file_sop_repository, mocks_setup, session_type, expected
    ) -> None:
        mocks_setup()
        result = local_file_sop_repository.get_sop(session_type=session_type)
        if callable(expected):
            expected(local_file_sop_repository)
        else:
            assert result == expected
