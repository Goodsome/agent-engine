from dataclasses import dataclass
from agent_engine.dispatching.domain.models import DispatchCommand, ExecutionReceipt
from agent_engine.dispatching.domain.ports.executor import AgentExecutorPort


@dataclass
class HandleDispatchCommand:
    """Dispatching 上下文的应用层用例：接收指令并驱动执行器"""

    executor: AgentExecutorPort

    async def execute(self, command: DispatchCommand) -> ExecutionReceipt:
        # 在此处可以增加校验、重试逻辑或超时控制（如果底层适配器未实现）
        return await self.executor.execute(command)
