from dataclasses import dataclass
from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from agent_engine.execution.domain.enums import ModelTier


@dataclass
class AgentGatewayRouter(AgentGateway):
    """根据默认提供商将请求路由到具体的网关。
    具体的网关实现负责将 ModelTier 映射到它们支持的具体模型名称。
    """

    claude_gateway: AgentGateway
    gemini_gateway: AgentGateway
    default_provider: str = "gemini"

    async def run(self, system_prompt: str, user_prompt: str, tools: list[str], model_tier: ModelTier | None = None) -> str:
        if self.default_provider == "claude":
            return await self.claude_gateway.run(system_prompt, user_prompt, tools, model_tier=model_tier)
        else:
            return await self.gemini_gateway.run(system_prompt, user_prompt, tools, model_tier=model_tier)
