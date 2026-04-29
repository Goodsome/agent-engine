from abc import ABC, abstractmethod
from agent_engine.dispatching.domain.value_objects.dispatch_command import DispatchCommand
from agent_engine.dispatching.domain.value_objects.execution_receipt import ExecutionReceipt


class AgentExecutorPort(ABC):
    """Agent 执行器接口：负责与底层模型 CLI 或 SDK 交互"""

    @abstractmethod
    async def execute(self, command: DispatchCommand) -> ExecutionReceipt:
        """执行派发指令并返回回执"""
        ...
