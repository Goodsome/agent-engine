from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from agent_engine.orchestration.domain.events.task_ready_event import TaskReadyEvent


class DomainEventListenerPort(ABC):
    """端口：领域事件监听器，以异步迭代器形式持续产出事件"""

    @abstractmethod
    def listen(self) -> AsyncIterator[TaskReadyEvent]:
        """持续监听并逐个产出领域事件"""
        ...

    @abstractmethod
    async def close(self) -> None:
        """优雅关闭接口"""
        ...
