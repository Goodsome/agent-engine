from pydantic import BaseModel, Field

class AgentProfile(BaseModel):
    scope_level: str
    role_name: str
    description: str
    role_prompt: str
    rules: dict[str, str] = Field(default_factory=dict)
