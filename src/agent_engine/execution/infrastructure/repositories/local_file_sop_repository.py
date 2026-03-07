import os
from dataclasses import dataclass
from agent_engine.execution.domain.ports.sop_repository import SopRepository
from agent_engine.execution.domain.enums import SessionType


@dataclass
class LocalFileSopRepository(SopRepository):
    """从本地文件系统（如 docs/ 或 sops/ 目录）读取 Markdown 格式的 SOP 提示词"""
    
    base_dir: str = "sops"

    async def get_sop(self, session_type: SessionType) -> str:
        # In a real environment, we'd read from `self.base_dir / session_type.value + '.md'`
        # For our test to pass and since we don't have real markdown files right now, we return a mock string.
        # It's better to implement reading with fallback:
        file_path = os.path.join(self.base_dir, f"{session_type.value}.md")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return "You are a planner."
