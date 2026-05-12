from pydantic import BaseModel


class ReviseTaskQuery(BaseModel):
    task_id: str
