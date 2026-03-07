import subprocess
from agent_engine.execution.domain.ports.agent_gateway import AgentGateway
from dataclasses import dataclass


@dataclass
class GeminiAgentGateway(AgentGateway):
    """封装对 Gemini Cli 的调用，将工具和 Prompt 注入并执行"""

    def run(self, system_prompt: str, user_prompt: str, tools: list[str]) -> str:
        prompt_text = f"{system_prompt}\n\n{user_prompt}"
        try:
            result = subprocess.run(
                ["gemini", "-p", prompt_text],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8"
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Gemini CLI failed with exit code {e.returncode}: {e.stderr}") from e
