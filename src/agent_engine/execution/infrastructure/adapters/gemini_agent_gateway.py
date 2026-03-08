import asyncio
from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from dataclasses import dataclass


@dataclass
class GeminiAgentGateway(AgentGateway):
    """封装对 Gemini Cli 的调用，将工具和 Prompt 注入并执行"""

    async def run(self, system_prompt: str, user_prompt: str, tools: list[str]) -> str:
        prompt_text = f"{system_prompt}\n---\n{user_prompt}"
        
        process = await asyncio.create_subprocess_exec(
            "gemini", "-p", prompt_text, "-y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Gemini CLI failed with exit code {process.returncode}: {stderr.decode('utf-8')}")
            
        return stdout.decode("utf-8").strip()
