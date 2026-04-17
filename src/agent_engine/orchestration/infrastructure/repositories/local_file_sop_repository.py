from agent_engine.orchestration.domain.ports.sop_repository import SopRepository
from agent_engine.orchestration.domain.value_objects.sop_content import SopContent
from uuid import UUID
from dataclasses import dataclass
from typing import Union


@dataclass
class LocalFileSopRepository(SopRepository):
    """从本地文件系统（sops/ 目录）读取带有 Frontmatter 的 Markdown 格式 SOP，并整理为 system_prompt"""

    base_dir: str | None = None

    async def get_sop(self, scope_level: str, architecture_layer: str | None = None) -> SopContent: ...

    def save(self, sop: Sop) -> None: ...

    def delete(self, sop_id: UUID) -> None: ...

    def find_by_id(self, sop_id: UUID) -> Sop | None: ...

    def _build_system_prompt(self, metadata: dict, content: str) -> str: ...
