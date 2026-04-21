from abc import ABC, abstractmethod
from agent_engine.dispatching.domain.models import DispatchCommand, ExecutionReceipt


class AgentExecutorPort(ABC):
    """Agent 执行器接口：负责与底层模型 CLI 或 SDK 交互"""

    @abstractmethod
    async def execute(self, command: DispatchCommand) -> ExecutionReceipt:
        """执行派发指令并返回回执"""
        ...
