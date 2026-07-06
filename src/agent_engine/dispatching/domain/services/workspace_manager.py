from dataclasses import dataclass
from pathlib import Path
from typing import Self

from agent_engine.dispatching.domain.exceptions.project_not_found import (
    ProjectNotFound,
)
from agent_engine.shared.domain.value_objects.project_id import ProjectId


@dataclass
class WorkspaceManager:
    """领域服务 — 管理项目工作目录的映射与解析。

    将项目与工作目录之间的映射规则作为领域概念内化，
    封装根据 ProjectId 获取对应文件系统工作路径的业务逻辑。
    """

    root_dir: Path

    def get_workspace(
        self: Self, 
        project_id: ProjectId,
        context: str | None = None
    ) -> Path:
        """根据项目标识解析并返回工作目录路径。

        Args:
            project_id: 目标项目的唯一标识。

        Returns:
            该项目对应的绝对文件系统路径。

        Raises:
            ProjectNotFound: 当 root_dir 下不存在与 project_id 对应的目录时。
        """
        workspace = (self.root_dir / project_id.value).resolve()

        if project_id.value == "pangu" and context:
            workspace = workspace / "contexts" / context

        if not workspace.exists():
            raise ProjectNotFound(project_id.value, root=workspace)

        return workspace
