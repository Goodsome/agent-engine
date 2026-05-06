import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import override

import frontmatter

from agent_engine.agent_registry.application.dtos.agent_profile import AgentProfile
from agent_engine.agent_registry.application.ports.agent_profile_query_service import (
    AgentProfileQueryService,
)

logger = logging.getLogger(__name__)


@dataclass
class LocalAgentProfileQueryService(AgentProfileQueryService):
    """基于本地 sops 目录查询 AgentProfile 的服务"""

    sops_dir: Path

    @override
    def get_profile(
        self,
        scope_level: str,
        architecture_layer: str | None = None,
    ) -> AgentProfile:
        main_file = os.path.join(self.sops_dir, f"{scope_level}.md")

        if not os.path.exists(main_file):
            raise FileNotFoundError(
                f"Agent profile not found for scope_level: {scope_level} at {main_file}"
            )

        post = frontmatter.load(main_file)
        role_name = str(post.metadata.get("name", ""))
        description = str(post.metadata.get("description", ""))
        role_prompt = str(post.content)

        rules: dict[str, str] = {}
        if scope_level in ("architecture", "component") and architecture_layer is not None:
            rule_file = os.path.join(self.sops_dir, f"{scope_level}_rule__{architecture_layer}.md")
            if os.path.exists(rule_file):
                with open(rule_file, "r", encoding="utf-8") as f:
                    rules[architecture_layer] = f.read()

        return AgentProfile(
            scope_level=scope_level,
            role_name=role_name,
            description=description,
            role_prompt=role_prompt,
            rules=rules,
        )
