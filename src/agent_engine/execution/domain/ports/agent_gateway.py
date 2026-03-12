from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from agent_engine.execution.domain.enums import ModelTier


class AgentGateway(ABC):
    """Agent 底层调用网关"""

    @abstractmethod
    async def run(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[str],
        model_tier: ModelTier | None = None,
    ) -> str:
        """执行 Agent 并返回完整响应"""
        ...

    @abstractmethod
    async def run_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[str],
        model_tier: ModelTier | None = None,
    ) -> AsyncIterator[str]:
        """流式执行 Agent 并返回文本块迭代器

        用于实时输出场景（如飞书消息流式更新）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入
            tools: 允许使用的工具列表
            model_tier: 模型档位 (PRO/FAST)

        Yields:
            文本块
        """
        ...
