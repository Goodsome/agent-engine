import json
import logging
import psycopg
from collections.abc import AsyncIterator

from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
from agent_engine.orchestration.domain.ports.domain_event_listener_port import (
    DomainEventListenerPort,
)

logger = logging.getLogger(__name__)


class PgNotifyEventListener(DomainEventListenerPort):
    """基于 PostgreSQL LISTEN/NOTIFY 的领域事件监听实现"""

    def __init__(self, dsn: str, channel: str):
        self._dsn = dsn
        self._channel = channel
        self._conn: psycopg.AsyncConnection | None = None

    async def listen(self) -> AsyncIterator[TaskReadyEvent]:
        dsn = self._dsn
        # 统一处理 SQLAlchemy 的 DSN 格式以兼容 psycopg 原生连接
        if dsn.startswith("postgresql+psycopg://"):
            dsn = dsn.replace("postgresql+psycopg://", "postgresql://", 1)

        self._conn = await psycopg.AsyncConnection.connect(dsn, autocommit=True)
        await self._conn.execute(f"LISTEN {self._channel}")
        logger.info(f"✅ PgNotifyEventListener 已连接到频道: '{self._channel}'")

        async for notify in self._conn.notifies():
            try:
                data = json.loads(notify.payload)
                if data.get("event_type") == "TaskReadyEvent":
                    yield TaskReadyEvent(**data)
            except Exception as e:
                # 添加异常保护，防止无效负载导致循环中断
                logger.error(f"❌ 解析事件载荷失败: {e}, payload: {notify.payload}")

    async def close(self) -> None:
        if self._conn and not self._conn.closed:
            await self._conn.close()
            logger.info("🛑 PgNotifyEventListener 连接已关闭")
