from agent_engine.shared.domain.core.domain_exception import DomainException
from typing import Self


class ProjectNotFound(DomainException):
    """项目未找到异常：当请求的 ProjectId 对应的项目不存在时抛出"""

    def __init__(self: Self, project_id: str) -> None:
        super().__init__(f"Project not found: {project_id}")
        self.project_id: str = project_id
