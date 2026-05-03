import os
import glob
import frontmatter

from agent_engine.agent_registry.application.dtos.agent_profile import AgentProfile
from agent_engine.agent_registry.application.ports.agent_profile_query_service import AgentProfileQueryService


class LocalQueryService(AgentProfileQueryService):
    """基于本地 sops 目录查询 AgentProfile 的服务"""

    def __init__(self, sops_dir: str):
        self.sops_dir = sops_dir

    def get_profile(self, scope_level: str) -> AgentProfile:
        main_file = os.path.join(self.sops_dir, f"{scope_level}.md")
        if not os.path.exists(main_file):
            raise FileNotFoundError(f"Agent profile not found for scope_level: {scope_level} at {main_file}")

        post = frontmatter.load(main_file)
        role_name = post.metadata.get("name", "")
        description = post.metadata.get("description", "")
        role_prompt = str(post.content)

        rules = {}
        if scope_level in ("architecture", "component"):
            pattern = os.path.join(self.sops_dir, f"{scope_level}_rule__*.md")
            for rule_file in glob.glob(pattern):
                filename = os.path.basename(rule_file)
                # extract architecture layer from filename, e.g., component_rule__application.md -> application
                layer_part = filename.replace(f"{scope_level}_rule__", "").replace(".md", "")
                
                with open(rule_file, "r", encoding="utf-8") as f:
                    rules[layer_part] = f.read()

        return AgentProfile(
            scope_level=scope_level,
            role_name=role_name,
            description=description,
            role_prompt=role_prompt,
            rules=rules
        )
