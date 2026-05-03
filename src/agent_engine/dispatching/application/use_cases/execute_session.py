from typing import Any
from pydantic import BaseModel, Field
from agent_engine.dispatching.domain.ports.executor import AgentExecutorPort
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.shared.domain.enums import ModelTier
from dataclasses import dataclass


class ExecuteSessionCommand(BaseModel):
    """执行会话指令：包含执行 Agent 所需的所有数据"""
    system_prompt: str
    user_prompt: str
    session_id: str
    model_tier: ModelTier | None = None
    tools: list[str] = Field(default_factory=lambda: ["Read", "Edit", "Glob"])
    context_payload: dict[str, Any] = Field(default_factory=dict)


class ExecuteSessionResult(BaseModel):
    """执行会话结果 DTO"""
    status: DispatchStatus
    output: str | None = None
    fault: str | None = None


@dataclass
class ExecuteSession:
    """Dispatching 上下文的应用层用例：接收指令并驱动执行器"""

    executor: AgentExecutorPort

    async def execute(self, command: ExecuteSessionCommand) -> ExecuteSessionResult:
        # 在此处可以增加校验、重试逻辑或超时控制（如果底层适配器未实现）
        receipt = await self.executor.execute(
            system_prompt=command.system_prompt,
            user_prompt=command.user_prompt,
            session_id=command.session_id,
            model_tier=command.model_tier,
            tools=command.tools,
            context_payload=command.context_payload,
        )
        return ExecuteSessionResult(
            status=receipt.status,
            output=receipt.output,
            fault=receipt.fault,
        )
