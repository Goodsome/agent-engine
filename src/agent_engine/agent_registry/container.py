from dependency_injector import containers
from dependency_injector.providers import Factory, Configuration
from pathlib import Path
import agent_engine


from agent_engine.agent_registry.infrastructure.adapters.local_agent_profile_query_service import (
    LocalAgentProfileQueryService,
)


class Container(containers.DeclarativeContainer):
    config: Configuration = Configuration()

    # 默认路径指向上下文内部的 sops 目录
    default_sops_dir: Path = Path(agent_engine.__file__).parent / "agent_registry" / "sops"

    agent_profile_query_service: Factory[LocalAgentProfileQueryService] = Factory(
        LocalAgentProfileQueryService,
        sops_dir=default_sops_dir,
    )
