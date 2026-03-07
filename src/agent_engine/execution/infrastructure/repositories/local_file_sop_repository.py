from dataclasses import dataclass
from agent_engine.execution.domain.ports.sop_repository import SopRepository
from agent_engine.execution.domain.enums import SessionType


@dataclass
class LocalFileSopRepository(SopRepository):
    """从本地文件系统（如 docs/ 或 sops/ 目录）读取 Markdown 格式的 SOP 提示词"""

    def get_sop(self, session_type: SessionType) -> str: ...
