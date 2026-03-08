import os
import frontmatter
from dataclasses import dataclass, field
from pathlib import Path
import agent_engine
from agent_engine.orchestration.domain.ports.sop_repository import SopRepository
from agent_engine.orchestration.domain.value_objects.sop_content import SopContent
from agent_engine.execution.domain.enums import ModelTier


@dataclass
class LocalFileSopRepository(SopRepository):
    """从本地文件系统（sops/ 目录）读取带有 Frontmatter 的 Markdown 格式 SOP，并整理为 system_prompt"""

    base_dir: str = field(default_factory=lambda: str(Path(agent_engine.__file__).parent / "sops"))

    async def get_sop(self, planning_level: str, status: str) -> SopContent:
        # Ensure values are used if they are Enums
        pl = getattr(planning_level, "value", planning_level)
        st = getattr(status, "value", status)
        filename = f"{pl}_{st}.md"
        file_path = os.path.join(self.base_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"SOP file not found: {file_path} "
                f"(planning_level={pl}, status={st})"
            )

        post = frontmatter.load(file_path)
        system_prompt = self._build_system_prompt(post.metadata, post.content)
        
        # Parse model tier from frontmatter
        raw_model = post.metadata.get("model")
        model_tier = None
        if raw_model:
            try:
                model_tier = ModelTier(raw_model.lower())
            except ValueError:
                # Fallback to PRO if unknown
                model_tier = ModelTier.PRO

        return SopContent(
            system_prompt=system_prompt,
            model_tier=model_tier
        )

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
