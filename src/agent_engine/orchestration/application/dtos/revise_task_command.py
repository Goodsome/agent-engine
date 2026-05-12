from pydantic import BaseModel


class ReviseTaskCommand(BaseModel):
    """重新修改任务指令"""

    task_id: str
