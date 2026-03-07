import pytest
from unittest.mock import MagicMock
from .cases_local_file_sop_repository import (
    TEST_CASES_DELETE,
    TEST_CASES_FIND_BY_ID,
    TEST_CASES_GET_SOP,
    TEST_CASES_SAVE,
)


class TestLocalFileSopRepository:

    @pytest.fixture
    def local_file_sop_repository(self) -> None:
        from agent_engine.execution.infrastructure.repositories.local_file_sop_repository import (
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

    @pytest.mark.parametrize("mocks_setup, sop, expected", TEST_CASES_SAVE)
    def test_save(self, local_file_sop_repository, mocks_setup, sop, expected) -> None:
        mocks_setup()
        result = local_file_sop_repository.save(sop=sop)
        if callable(expected):
            expected(local_file_sop_repository)
        else:
            assert result == expected

    @pytest.mark.parametrize("mocks_setup, sop_id, expected", TEST_CASES_DELETE)
    def test_delete(
        self, local_file_sop_repository, mocks_setup, sop_id, expected
    ) -> None:
        mocks_setup()
        result = local_file_sop_repository.delete(sop_id=sop_id)
        if callable(expected):
            expected(local_file_sop_repository)
        else:
            assert result == expected

    @pytest.mark.parametrize("mocks_setup, sop_id, expected", TEST_CASES_FIND_BY_ID)
    def test_find_by_id(
        self, local_file_sop_repository, mocks_setup, sop_id, expected
    ) -> None:
        mocks_setup()
        result = local_file_sop_repository.find_by_id(sop_id=sop_id)
        if callable(expected):
            expected(local_file_sop_repository)
        else:
            assert result == expected
