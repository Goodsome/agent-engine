import asyncio
from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from dataclasses import dataclass
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


@dataclass
class ClaudeAgentGateway(AgentGateway):
    """封装对 Claude Agent SDK 的调用，将工具和 Prompt 注入并执行"""

    def run(self, system_prompt: str, user_prompt: str, tools: list[str]) -> str:
        prompt = f"{system_prompt}\n\n{user_prompt}"
        allowed_tools = tools if tools else ["Read", "Edit", "Glob"]
        
        async def _run_agent() -> str:
            output_text = []
            async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    allowed_tools=allowed_tools,
                    permission_mode="acceptEdits"
                )
            ):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if hasattr(block, "text"):
                            output_text.append(block.text)
                # Ignore ResultMessage for now, as we just want the text output
            return "\n".join(output_text)
            
        return asyncio.run(_run_agent())
