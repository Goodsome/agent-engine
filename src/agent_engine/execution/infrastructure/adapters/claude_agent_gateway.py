import asyncio
from collections.abc import AsyncIterator
from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from agent_engine.execution.domain.enums import ModelTier
from dataclasses import dataclass
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


@dataclass
class ClaudeAgentGateway(AgentGateway):
    """封装对 Claude Agent SDK 的调用，将工具和 Prompt 注入并执行"""

    async def run(self, system_prompt: str, user_prompt: str, tools: list[str], model_tier: ModelTier | None = None) -> str:
        prompt = f"{system_prompt}\n---\n{user_prompt}"
        allowed_tools = tools if tools else ["Read", "Edit", "Glob"]

        model = None
        if model_tier == ModelTier.PRO:
            model = "opus"
        elif model_tier == ModelTier.FAST:
            model = "sonnet"

        output_text = []
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=allowed_tools,
                permission_mode="bypassPermissions",
                model=model,
            )
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        output_text.append(block.text)
            # Ignore ResultMessage for now, as we just want the text output
        return "\n".join(output_text)

    async def run_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[str],
        model_tier: ModelTier | None = None,
    ) -> AsyncIterator[str]:
        """流式执行 Agent 并返回文本块迭代器

        用于实时输出场景（如飞书消息流式更新）
        """
        prompt = f"{system_prompt}\n---\n{user_prompt}"
        allowed_tools = tools if tools else ["Read", "Edit", "Glob"]

        model = None
        if model_tier == ModelTier.PRO:
            model = "opus"
        elif model_tier == ModelTier.FAST:
            model = "sonnet"

        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=allowed_tools,
                permission_mode="acceptEdits",
                model=model,
            )
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        yield block.text
