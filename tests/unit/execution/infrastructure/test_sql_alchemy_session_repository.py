import pytest
from unittest.mock import MagicMock
from .cases_sql_alchemy_session_repository import (
    TEST_CASES_DELETE,
    TEST_CASES_FIND_BY_ID,
    TEST_CASES_SAVE,
)


class TestSqlAlchemySessionRepository:

    @pytest.fixture
    def sql_alchemy_session_repository(self) -> None:
        from agent_engine.execution.infrastructure.repositories.sql_alchemy_session_repository import (
            SqlAlchemySessionRepository,
        )

        return SqlAlchemySessionRepository()

    @pytest.mark.parametrize("mocks_setup, session, expected", TEST_CASES_SAVE)
    async def test_save(
        self, sql_alchemy_session_repository, mocks_setup, session, expected
    ) -> None:
        mocks_setup()
        result = await sql_alchemy_session_repository.save(session=session)
        if callable(expected):
            expected(sql_alchemy_session_repository)
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "mocks_setup, agent_session_id, expected", TEST_CASES_DELETE
    )
    async def test_delete(
        self, sql_alchemy_session_repository, mocks_setup, agent_session_id, expected
    ) -> None:
        mocks_setup()
        result = await sql_alchemy_session_repository.delete(
            agent_session_id=agent_session_id
        )
        if callable(expected):
            expected(sql_alchemy_session_repository)
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "mocks_setup, agent_session_id, expected", TEST_CASES_FIND_BY_ID
    )
    async def test_find_by_id(
        self, sql_alchemy_session_repository, mocks_setup, agent_session_id, expected
    ) -> None:
        mocks_setup()
        result = await sql_alchemy_session_repository.find_by_id(
            agent_session_id=agent_session_id
        )
        if callable(expected):
            expected(sql_alchemy_session_repository)
        else:
            assert result == expected
