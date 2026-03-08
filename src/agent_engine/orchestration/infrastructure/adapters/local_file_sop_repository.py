import os
import frontmatter
from dataclasses import dataclass, field
from pathlib import Path
import agent_engine
from agent_engine.orchestration.domain.ports.sop_repository import SopRepository


@dataclass
class LocalFileSopRepository(SopRepository):
    """从本地文件系统（sops/ 目录）读取带有 Frontmatter 的 Markdown 格式 SOP，并整理为 system_prompt"""

    base_dir: str = field(default_factory=lambda: str(Path(agent_engine.__file__).parent / "sops"))

    async def get_sop(self, planning_level: str, status: str) -> str:
        filename = f"{planning_level}_{status}.md"
        file_path = os.path.join(self.base_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"SOP file not found: {file_path} "
                f"(planning_level={planning_level}, status={status})"
            )

        post = frontmatter.load(file_path)
        return self._build_system_prompt(post.metadata, post.content)

    @staticmethod
    def _build_system_prompt(metadata: dict, content: str) -> str:
        """将 SOP Frontmatter 数据和 Markdown 内容整理为完整的 system_prompt 字符串"""
        parts: list[str] = []

        # 1. Persona/Role Definition
        name = metadata.get("name")
        desc = metadata.get("description")
        if name or desc:
            role_parts = []
            if name:
                role_parts.append(f"Name: {name}")
            if desc:
                role_parts.append(f"Description: {desc}")
            parts.append(f"# Role Definition\n" + "\n".join(role_parts))

        # 2. Allowed Tools (metadata)
        if tools := metadata.get("tools"):
            if isinstance(tools, list):
                tools_text = ", ".join(tools)
            else:
                tools_text = str(tools)
            parts.append(f"# Allowed Tools\n{tools_text}")

        # 3. Main Content
        if content and content.strip():
            # If content starts with a title that might be redundant, 
            # we just keep it as is since it's the core SOP.
            parts.append(content.strip())

        # 4. Fallback/Extra Metadata (if any specific ones like 'checklist' are in metadata instead of content)
        for key in ["goal", "guidance", "constraints", "checklist"]:
            if val := metadata.get(key):
                if isinstance(val, list):
                    val_text = "\n".join(f"- {item}" for item in val)
                else:
                    val_text = str(val)
                # Avoid duplicates if they are already in the content (simple check)
                if val_text[:50] not in content:
                    parts.append(f"# {key.capitalize()}\n{val_text}")

        return "\n\n".join(parts)
