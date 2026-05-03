from enum import Enum

class ScopeLevel(Enum):
    """
    Defines the delegation level of the task, mapping directly to Agent roles and context boundaries.
    """

    PROJECT = "project"  # PM/系统架构师：负责跨上下文的需求路由与最终交付
    CONTEXT = "context"  # 领域专家：负责单一上下文内的业务分析与架构拆解
    ARCHITECTURE = "architecture"  # 技术负责人：负责特定上下文的代码架构设计与原子任务派发
    COMPONENT = "component"  # 程序员：负责单一职责的代码落地


class ArchitectureLayer(Enum):
    """DDD architecture layers."""

    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    INTERFACES = "interfaces"
    CROSS_CUTTING = "cross_cutting"  # 横切关注点，如日志、通用配置
