import logging
from pathlib import Path
from dataclasses import dataclass
from agent_engine.dispatching.domain.ports.agent_executor_port import AgentExecutorPort
from agent_engine.dispatching.application.dtos.execute_session_command import (
    ExecuteSessionCommand,
)
from agent_engine.dispatching.application.dtos.execute_session_result import (
    ExecuteSessionResult,
)
from typing import Self

logger = logging.getLogger(__name__)


@dataclass
class ExecuteSession:
    """Dispatching 上下文的应用层用例：接收指令并驱动执行器"""

    executor: AgentExecutorPort

    async def execute(
        self: Self, command: ExecuteSessionCommand
    ) -> ExecuteSessionResult:
        logger.info(f"Executing session: {command.session_id}")
        if command.project_id:
            cwd = Path("/Users/xxxx/Projects") / command.project_id
        else:
            cwd = None
        receipt = await self.executor.execute(
            system_prompt=command.system_prompt,
            user_prompt=command.user_prompt,
            session_id=command.session_id,
            model_tier=command.model_tier,
            tools=command.tools,
            context_payload=command.context_payload,
            cwd=cwd,
        )
        return ExecuteSessionResult(
            status=receipt.status, output=receipt.output, fault=receipt.fault
        )
