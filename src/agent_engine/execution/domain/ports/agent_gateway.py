from abc import ABC, abstractmethod


class AgentGateway(ABC):
    """Agent 底层调用网关 (封装 claude-agent-sdk)"""

    @abstractmethod
    def run(self, system_prompt: str, user_prompt: str, tools: list[str]) -> str: ...
