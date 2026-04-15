import json
import logging
from typing import override, Any
import psycopg
import asyncio

from psycopg import sql
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent
from agent_engine.orchestration.domain.events.task_review_requested_event import TaskReviewRequestedEvent
from agent_engine.orchestration.domain.ports.domain_event_listener_port import (
    DomainEventListenerPort,
    DispatchableTaskEvent,
)

from pydantic import PostgresDsn

logger = logging.getLogger(__name__)


@dataclass
class PgNotifyEventListener(DomainEventListenerPort):
    """基于 PostgreSQL LISTEN/NOTIFY 的领域事件监听实现"""
    dsn: str | PostgresDsn
    channel: str
    _stop_event: asyncio.Event = field(default_factory=asyncio.Event)
    
    
    @override
    async def listen(self) -> AsyncIterator[DispatchableTaskEvent]:
        dsn = str(self.dsn)

        while not self._stop_event.is_set():
            try:
                async with await psycopg.AsyncConnection.connect(dsn, autocommit=True) as conn:
                    query = sql.SQL("LISTEN {channel}").format(
                        channel=sql.Identifier(self.channel)
                    )
                    _ = await conn.execute(query)
                    async for notify in conn.notifies():
                        if self._stop_event.is_set():
                            break
                        data: dict[str, Any] = json.loads(notify.payload)
                        event_type = data.get("event_type")
                        if event_type == "TaskReadyEvent":
                            yield TaskReadyEvent.model_validate(data)
                        elif event_type == "TaskReviewRequestedEvent":
                            yield TaskReviewRequestedEvent.model_validate(data)
            except (psycopg.OperationalError, Exception) as e:
                if self._stop_event.is_set():
                    break
                logger.error(f"📡 连接异常: {e}，准备重连...")
                await asyncio.sleep(5)

    @override
    async def close(self) -> None:
        """优雅停止"""
        self._stop_event.set()