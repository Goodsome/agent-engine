from pydantic import BaseModel
from agent_engine.integration.domain.value_objects.feishu_message_payload import (
    FeishuMessagePayload,
)


class HandleFeishuMessageCommand(BaseModel):
    payload: FeishuMessagePayload
