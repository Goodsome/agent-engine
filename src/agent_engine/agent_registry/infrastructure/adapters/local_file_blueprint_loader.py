import os
from typing import Any
import frontmatter
from dataclasses import dataclass

from agent_engine.agent_registry.domain.models import ExecutionBlueprint
from agent_engine.agent_registry.domain.ports.blueprint_registry import BlueprintRegistryPort
from agent_engine.shared.domain.enums import ModelTier


@dataclass
class LocalMarkdownBlueprintLoader(BlueprintRegistryPort):
    """基于本地 Markdown 文件的蓝图加载器"""

    base_dir: str

    async def get_blueprint(
        self, scope_level: str, architecture_layer: str | None = None
    ) -> ExecutionBlueprint:
        sl = str(getattr(scope_level, "value", scope_level))

        if sl == "architectural" and architecture_layer:
            al = str(getattr(architecture_layer, "value", architecture_layer))
            filename = f"architectural_{al.lower()}.md"
        else:
            filename = f"{sl.lower()}.md"

        file_path = os.path.join(self.base_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Blueprint file not found: {file_path} "
                f"(scope_level={sl}, architecture_layer={architecture_layer})"
            )

        post = frontmatter.load(file_path)
        system_prompt = self._build_system_prompt(post.metadata, str(post.content))

        # Parse model tier from frontmatter
        raw_model = post.metadata.get("model")
        model_tier = None
        if isinstance(raw_model, str):
            try:
                model_tier = ModelTier(raw_model.lower())
            except ValueError:
                model_tier = ModelTier.PRO

        return ExecutionBlueprint(
            system_prompt=system_prompt,
            model_tier=model_tier
        )

    @staticmethod
    def _build_system_prompt(metadata: dict[str, Any], content: str) -> str:
        """将 SOP Frontmatter 数据 and Markdown 内容整理为完整的 system_prompt 字符串"""
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
            parts.append("# Role Definition\n" + "\n".join(role_parts))


        # 2. Allowed Tools (metadata)
        if tools := metadata.get("tools"):
            if isinstance(tools, list):
                tools_text = ", ".join(tools)
            else:
                tools_text = str(tools)
            parts.append(f"# Allowed Tools\n{tools_text}")

        # 3. Main Content
        if content and content.strip():
            parts.append(content.strip())

        # 4. Fallback/Extra Metadata
        for key in ["goal", "guidance", "constraints", "checklist"]:
            if val := metadata.get(key):
                if isinstance(val, list):
                    val_text = "\n".join(f"- {item}" for item in val)
                else:
                    val_text = str(val)
                if val_text[:50] not in content:
                    parts.append(f"# {key.capitalize()}\n{val_text}")

        return "\n\n".join(parts)
