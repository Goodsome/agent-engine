import logging
from dataclasses import dataclass, field
from claude_agent_sdk import query, ClaudeAgentOptions
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.dispatching.domain.value_objects.dispatch_command import DispatchCommand
from agent_engine.dispatching.domain.value_objects.execution_receipt import ExecutionReceipt
from agent_engine.dispatching.domain.ports.executor import AgentExecutorPort
from agent_engine.shared.domain.enums import ModelTier

logger = logging.getLogger(__name__)

@dataclass
class ClaudeAgentExecutorAdapter(AgentExecutorPort):
    """适配 Claude Agent SDK 的执行器"""

    _stderr_output: list[str] = field(default_factory=list)

    def _stderr_callback(self, line: str) -> None:
        self._stderr_output.append(line)

    async def execute(self, command: DispatchCommand) -> ExecutionReceipt:
        prompt = f"{command.system_prompt}\n---\n{command.user_prompt}"
        
        model = None
        if command.model_tier == ModelTier.PRO:
            model = "opus"
        elif command.model_tier == ModelTier.FAST:
            model = "sonnet"

        self._stderr_output.clear()
        output_text = []

        try:
            async for message in query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    session_id=command.session_id,
                    allowed_tools=command.tools,
                    permission_mode="bypassPermissions",
                    model=model,
                    stderr=self._stderr_callback,
                    setting_sources=["user", "project"]
                )
            ):
                if hasattr(message, "content"):
                    content = message.content
                    if isinstance(content, list):
                        # Handle list of blocks (ThinkingBlock, TextBlock, etc.)
                        for block in content:
                            if hasattr(block, "text"):
                                output_text.append(str(block.text))
                            elif hasattr(block, "thinking"):
                                # Optionally log thinking
                                pass
                    elif isinstance(content, str):
                        output_text.append(content)
            
            final_output = "".join(output_text)
            return ExecutionReceipt(
                status=DispatchStatus.SUCCESS,
                output=final_output
            )
        except Exception as e:
            logger.error(f"Claude execution failed: {e}")
            return ExecutionReceipt(
                status=DispatchStatus.FAULT,
                fault=str(e)
            )
