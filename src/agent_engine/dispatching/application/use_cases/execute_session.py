import logging
from pathlib import Path 
from pydantic import BaseModel, Field
from dataclasses import dataclass

from agent_engine.dispatching.domain.ports.agent_executor_port import AgentExecutorPort
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.shared.domain.enums import ModelTier

logger = logging.getLogger(__name__)

class ExecuteSessionCommand(BaseModel):
    """执行会话指令：包含执行 Agent 所需的所有数据"""
    system_prompt: str
    user_prompt: str
    session_id: str
    project_id: str | None = None
    model_tier: ModelTier | None = None
    tools: list[str] = Field(default_factory=lambda: ["Read", "Edit", "Glob"])
    context_payload: dict[str, str | None] = Field(default_factory=dict)


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
        logger.info(f"Executing session: {command.session_id}")
        if command.project_id:
            cwd = Path("/Users/xxxx/Projects") / command.project_id
        else:
            cwd = None
        receipt = await self.executor.execute(
            system_prompt=command.system_prompt,
            user_prompt=command.user_prompt,
            session_id=command.session_id,
            model_tier=command.model_tier,
            tools=command.tools,
            context_payload=command.context_payload,
            cwd=cwd
        )
        return ExecuteSessionResult(
            status=receipt.status,
            output=receipt.output,
            fault=receipt.fault,
        )
