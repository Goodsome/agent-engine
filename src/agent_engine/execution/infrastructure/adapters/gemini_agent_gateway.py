import asyncio
from collections.abc import AsyncIterator
from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from agent_engine.execution.domain.enums import ModelTier
from dataclasses import dataclass


@dataclass
class GeminiAgentGateway(AgentGateway):
    """封装对 Gemini Cli 的调用，将工具和 Prompt 注入并执行"""

    async def run(self, system_prompt: str, user_prompt: str, tools: list[str], model_tier: ModelTier | None = None) -> str:
        prompt_text = f"{system_prompt}\n---\n{user_prompt}"

        args = ["gemini", "-p", prompt_text, "-y"]
        if model_tier:
            # model_name = "gemini-3.1-pro-preview" if model_tier == ModelTier.PRO else "gemini-3-flash-preview"
            model_name = "pro" if model_tier == ModelTier.PRO else "flash"
            args.extend(["--model", model_name])

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Gemini CLI failed with exit code {process.returncode}: {stderr.decode('utf-8')}")

        return stdout.decode("utf-8").strip()

    async def run_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[str],
        model_tier: ModelTier | None = None,
    ) -> AsyncIterator[str]:
        """流式执行 Agent 并返回文本块迭代器

        注意: Gemini CLI 不支持真正的流式输出，
        当前实现为一次性返回完整结果作为单个块。
        TODO: 研究是否有 Gemini API 支持真正的流式输出
        """
        # Gemini CLI 不支持真正的流式，先获取完整结果再yield
        result = await self.run(system_prompt, user_prompt, tools, model_tier)
        yield result
