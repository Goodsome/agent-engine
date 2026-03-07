from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from dataclasses import dataclass


@dataclass
class GeminiAgentGateway(AgentGateway):
    """封装对 Gemini Cli 的调用，将工具和 Prompt 注入并执行"""

    def run(self, system_prompt: str, user_prompt: str, tools: list[str]) -> str:
        # Mocked CLI call
        return "Mocked Gemini Response"
