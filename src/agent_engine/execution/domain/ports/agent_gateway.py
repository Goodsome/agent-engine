from abc import ABC, abstractmethod
from agent_engine.execution.domain.enums import ModelTier


class AgentGateway(ABC):
    """Agent 底层调用网关"""

    @abstractmethod
    async def run(self, system_prompt: str, user_prompt: str, tools: list[str], model_tier: ModelTier | None = None) -> str: ...
