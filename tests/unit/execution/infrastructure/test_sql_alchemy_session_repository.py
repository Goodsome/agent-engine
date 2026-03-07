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
        from agent_engine.execution.infrastructure.sql_alchemy_session_repository import (
            SqlAlchemySessionRepository,
        )

        return SqlAlchemySessionRepository()

    @pytest.mark.parametrize("mocks_setup, session, expected", TEST_CASES_SAVE)
    def test_save(
        self, sql_alchemy_session_repository, mocks_setup, session, expected
    ) -> None:
        mocks_setup()
        result = sql_alchemy_session_repository.save(session=session)
        if callable(expected):
            expected(sql_alchemy_session_repository)
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "mocks_setup, agent_session_id, expected", TEST_CASES_DELETE
    )
    def test_delete(
        self, sql_alchemy_session_repository, mocks_setup, agent_session_id, expected
    ) -> None:
        mocks_setup()
        result = sql_alchemy_session_repository.delete(
            agent_session_id=agent_session_id
        )
        if callable(expected):
            expected(sql_alchemy_session_repository)
        else:
            assert result == expected

    @pytest.mark.parametrize(
        "mocks_setup, agent_session_id, expected", TEST_CASES_FIND_BY_ID
    )
    def test_find_by_id(
        self, sql_alchemy_session_repository, mocks_setup, agent_session_id, expected
    ) -> None:
        mocks_setup()
        result = sql_alchemy_session_repository.find_by_id(
            agent_session_id=agent_session_id
        )
        if callable(expected):
            expected(sql_alchemy_session_repository)
        else:
            assert result == expected
