from enum import Enum


class SessionStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class ModelTier(str, Enum):
    """模型能力档位定义"""
    PRO = "pro"     # 高性能/高智商模型
    FAST = "fast"   # 快速响应模型
