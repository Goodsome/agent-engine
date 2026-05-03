from abc import ABC, abstractmethod
from typing import Any
from agent_engine.dispatching.domain.value_objects.execution_receipt import ExecutionReceipt
from agent_engine.shared.domain.enums import ModelTier


class AgentExecutorPort(ABC):
    """Agent 执行器接口：负责与底层模型 CLI 或 SDK 交互"""

    @abstractmethod
    async def execute(
        self,
        system_prompt: str,
        user_prompt: str,
        session_id: str,
        model_tier: ModelTier | None = None,
        tools: list[str] | None = None,
        context_payload: dict[str, Any] | None = None,
    ) -> ExecutionReceipt:
        """执行派发指令并返回回执"""
        ...
