import logging
import json
from typing import override
from dataclasses import dataclass, field
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    UserMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    get_session_info
)
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.dispatching.domain.value_objects.execution_receipt import ExecutionReceipt
from agent_engine.dispatching.domain.ports.agent_executor_port import AgentExecutorPort
from agent_engine.shared.domain.enums import ModelTier

logger = logging.getLogger(__name__)

@dataclass
class ClaudeAgentExecutorAdapter(AgentExecutorPort):
    """适配 Claude Agent SDK 的执行器"""

    _stderr_output: list[str] = field(default_factory=list)

    def _stderr_callback(self, line: str) -> None:
        self._stderr_output.append(line)

    @override
    async def execute(
        self,
        system_prompt: str,
        user_prompt: str,
        session_id: str,
        model_tier: ModelTier | None = None,
        tools: list[str] | None = None,
        context_payload: dict[str, str | None] | None = None,
        cwd: str | None = None,
    ) -> ExecutionReceipt:
        prompts: list[str] = []
        if system_prompt:
            prompts.append(system_prompt)
        prompts.append(user_prompt)
        if context_payload:
            prompts.append(json.dumps(context_payload, indent=2))
            
        prompt = "\n---\n".join(prompts)
        
        model = None
        if model_tier == ModelTier.PRO:
            model = "opus"
        elif model_tier == ModelTier.FAST:
            model = "sonnet"

        self._stderr_output.clear()
        output_text: list[str] = []

        try:
            # 检查会话是否存在以决定是 resume 还是新开 session
            session_info = get_session_info(session_id)
            # 如果会话已存在，使用 resume 恢复并置 session_id 为 None；
            # 否则使用 session_id 指定新会话 ID 并置 resume 为 None。
            resume_val = session_id if session_info else None
            sid_val = None if session_info else session_id
            options = ClaudeAgentOptions(
                session_id=sid_val,
                resume=resume_val,
                permission_mode="bypassPermissions",
                model=model,
                stderr=self._stderr_callback,
                setting_sources=["user", "project"],
                cwd=cwd,
            )
            async with ClaudeSDKClient(options=options) as client:
                await client.query(prompt=prompt)
                async for message in client.receive_response():
                    if isinstance(message, (AssistantMessage, UserMessage)):
                        content = message.content
                        if isinstance(content, list):
                            # Handle list of blocks (ThinkingBlock, TextBlock, etc.)
                            for block in content:
                                if isinstance(block, TextBlock):
                                    output_text.append(str(block.text))
                                elif isinstance(block, ThinkingBlock):
                                    # Optionally log thinking
                                    pass
                        else:
                            # basedpyright says isinstance(content, str) is redundant
                            output_text.append(str(content))
                    elif isinstance(message, ResultMessage):
                        logger.info(f"Execution finished for session: {message.session_id}")
            
            final_output = "".join(output_text)
            return ExecutionReceipt(
                status=DispatchStatus.SUCCESS,
                output=final_output
            )
        except Exception as e:
            stderr_msg = "".join(self._stderr_output)
            error_detail = f"{e}\nStderr: {stderr_msg}" if stderr_msg else str(e)
            logger.error(f"Claude execution failed: {error_detail}")
            return ExecutionReceipt(
                status=DispatchStatus.FAULT,
                fault=error_detail
            )
