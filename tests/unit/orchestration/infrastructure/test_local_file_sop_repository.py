import pytest
from .cases_local_file_sop_repository import TEST_CASES_GET_SOP

class TestLocalFileSopRepository:

    @pytest.fixture
    def local_file_sop_repository(self) -> None:
        from agent_engine.orchestration.infrastructure.adapters.local_file_sop_repository import (
            LocalFileSopRepository,
        )
        # Pointing to the real `sops/` directory for this test by default
        return LocalFileSopRepository()

    @pytest.mark.parametrize("mocks_setup, planning_level, status, expected", TEST_CASES_GET_SOP)
    async def test_get_sop(self, local_file_sop_repository, mocks_setup, planning_level, status, expected) -> None:
        mocks_setup()
        result = await local_file_sop_repository.get_sop(planning_level=planning_level, status=status)
        if callable(expected):
            assert expected(result)
        else:
            assert result == expected
