from enum import Enum


class SessionType(Enum):
    """执行会话类型"""

    PLANNER = "planner"
    EXECUTOR = "executor"


class SessionStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
