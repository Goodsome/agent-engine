from abc import ABC, abstractmethod
from agent_engine.agent_registry.domain.models import ExecutionBlueprint


class BlueprintRegistryPort(ABC):
    """蓝图注册中心接口：负责根据上下文标识符查询执行蓝图"""

    @abstractmethod
    async def get_blueprint(
        self, scope_level: str, architecture_layer: str | None = None
    ) -> ExecutionBlueprint:
        """获取指定层级和范围的执行蓝图"""
        ...
