from agent_engine.shared.domain.value_objects.session_id import SessionId
from pydantic import BaseModel
from agent_engine.integration.domain.value_objects.feishu_message_id import (
    FeishuMessageId,
)


class HandleFeishuMessageResult(BaseModel):
    reply_message_id: FeishuMessageId
    session_id: SessionId
