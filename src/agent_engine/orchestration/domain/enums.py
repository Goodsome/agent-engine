from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionLifeCycle(str, Enum):
    OPEN = "open"
    

class SessionStatus(str, Enum):
    IDLE = "idle"
    PROCESSING = "processing"


class TaskStatus(str, Enum):
    """The lifecycle state of a task."""

    PENDING = "pending"

    BLOCKED = "blocked"

    READY = "ready"

    IN_PROGRESS = "in_progress"

    REVIEW = "review"

    DONE = "done"

    CHANGES_REQUESTED = "changes_requested"

    SKIPPED = "skipped"

    DISCARDED = "discarded"


class PlanningLevel(str, Enum):
    """Defines the uncertainty and granularity of the task."""

    INITIATIVE = "initiative"

    MILESTONE = "milestone"

    ARCHITECTURAL = "architectural"

    FEATURE = "feature"

    ATOMIC = "atomic"


class ScopeLevel(str, Enum):
    """
    Defines the delegation level of the task, mapping directly to Agent roles and context boundaries.
    """
    PROJECT = "project"             # PM/系统架构师：负责跨上下文的需求路由与最终交付
    CONTEXT = "context"             # 领域专家：负责单一上下文内的业务分析与架构拆解
    ARCHITECTURAL = "architectural" # 技术负责人：负责特定代码分层的技术设计与原子任务派发
    ATOMIC = "atomic"               # 程序员：负责单一职责的代码落地

