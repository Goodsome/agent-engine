from dependency_injector import containers, providers
from dependency_injector.providers import Factory
from pathlib import Path
import agent_engine
from agent_engine.agent_registry.infrastructure.adapters.local_file_blueprint_loader import (
    LocalMarkdownBlueprintLoader,
)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # 默认路径指向上下文内部的 sops 目录
    default_sops_dir = str(Path(agent_engine.__file__).parent / "agent_registry" / "sops")

    blueprint_registry = Factory(
        LocalMarkdownBlueprintLoader,
        base_dir=config.SOPS_DIR.if_not_none(default_sops_dir),
    )
