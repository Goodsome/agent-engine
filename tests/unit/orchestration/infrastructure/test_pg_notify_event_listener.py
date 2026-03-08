import pytest
from pydantic import PostgresDsn
from unittest.mock import AsyncMock, patch
from agent_engine.orchestration.infrastructure.adapters.pg_notify_event_listener import PgNotifyEventListener

@pytest.mark.asyncio
async def test_listen_with_postgres_dsn_object_fixed():
    # 模拟一个 PostgresDsn 对象
    dsn = PostgresDsn("postgresql+psycopg://user:pass@localhost:5432/db")
    listener = PgNotifyEventListener(dsn=dsn, channel="test_channel")
    
    # 我们 mock psycopg.AsyncConnection.connect，以防真的建立数据库连接
    with patch("psycopg.AsyncConnection.connect", new_callable=AsyncMock) as mock_connect:
        mock_conn = AsyncMock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn
        
        # 此时 listen() 应该不再抛出 AttributeError
        it = listener.listen()
        try:
            # 触发迭代器
            await it.__anext__()
        except StopAsyncIteration:
            pass
        except Exception:
            pass
            
        # 验证 connect 被调用的 DSN 已经被转换且修正了前缀
        mock_connect.assert_called_once()
        called_dsn = mock_connect.call_args[0][0]
        assert isinstance(called_dsn, str)
        assert called_dsn.startswith("postgresql://")
        assert not called_dsn.startswith("postgresql+psycopg://")

@pytest.mark.asyncio
async def test_listen_with_string_dsn():
    dsn = "postgresql://user:pass@localhost:5432/db"
    listener = PgNotifyEventListener(dsn=dsn, channel="test_channel")
    
    with patch("psycopg.AsyncConnection.connect", new_callable=AsyncMock) as mock_connect:
        mock_conn = AsyncMock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn
        
        it = listener.listen()
        try:
            await it.__anext__()
        except StopAsyncIteration:
            pass
        except Exception:
            pass
            
        mock_connect.assert_called_once_with(dsn, autocommit=True)
