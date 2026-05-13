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
from agent_engine.dispatching.domain.services.workspace_manager import WorkspaceManager
from agent_engine.shared.domain.value_objects.project_id import ProjectId

logger = logging.getLogger(__name__)


@dataclass
class ExecuteSession:
    """Dispatching 上下文的应用层用例：接收指令并驱动执行器"""

    executor: AgentExecutorPort
    workspace_manager: WorkspaceManager

    async def execute(
        self: Self, command: ExecuteSessionCommand
    ) -> ExecuteSessionResult:
        logger.info(f"Executing session: {command.session_id}")
        cwd = self._resolve_cwd(command.project_id)
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

    def _resolve_cwd(self: Self, project_id: str | None) -> Path | None:
        """根据 project_id 解析工作目录。

        当 project_id 非空时，委托 WorkspaceManager 解析路径；
        否则返回 None。ProjectNotFound 异常不做捕获，自然向上传播。
        """
        if not project_id:
            return None
        return self.workspace_manager.get_workspace(
            ProjectId(value=project_id)
        )
