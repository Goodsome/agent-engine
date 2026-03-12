import json
import uuid
from dataclasses import dataclass
from agent_engine.integration.domain.ports.conversation_context_repository import (
    ConversationContextRepository,
)
from agent_engine.integration.domain.value_objects.feishu_message_payload import (
    FeishuMessagePayload,
)
from agent_engine.orchestration.domain.ports.execution_trigger_port import (
    ExecutionTriggerPort,
)
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.shared.domain.value_objects.job_id import JobId
from agent_engine.integration.domain.ports.feishu_client_port import FeishuClientPort
from pydantic import BaseModel
from agent_engine.integration.domain.value_objects.feishu_message_id import (
    FeishuMessageId,
)
from agent_engine.integration.domain.enums import ChatType


class HandleFeishuMessageCommand(BaseModel):
    payload: FeishuMessagePayload


class HandleFeishuMessageResult(BaseModel):
    reply_message_id: FeishuMessageId
    session_id: SessionId


@dataclass
class HandleFeishuMessage:
    """处理飞书消息 - 非流式响应

    流程:
    1. 获取或创建会话上下文
    2. 生成虚拟 JobId (防腐层)
    3. 触发 Agent 执行
    4. 根据聊天类型路由回复 (P2P 发送新消息, GROUP 回复消息)
    5. 更新会话上下文
    """

    feishu_client: FeishuClientPort
    execution_trigger: ExecutionTriggerPort
    context_repo: ConversationContextRepository

    async def execute(self, cmd: HandleFeishuMessageCommand) -> HandleFeishuMessageResult:
        payload = cmd.payload

        # 1. 获取或创建会话上下文
        context = await self.context_repo.find_by_chat_id(payload.chat_id)
        if context is None:
            from agent_engine.integration.domain.aggregates.conversation_context import (
                ConversationContext,
            )
            context = ConversationContext.create(payload.chat_id)

        # 添加用户消息到历史
        context.add_message("user", payload.content)

        # 2. 生成虚拟 JobId (防腐层 - 标识来自即时通讯渠道)
        synthetic_job_id = JobId.create()

        # 3. 构建 system prompt (包含对话历史)
        system_prompt = self._build_system_prompt(context)

        # 4. 触发 Agent 执行
        result = await self.execution_trigger.trigger_session(
            job_id=synthetic_job_id,
            system_prompt=system_prompt,
            requirement=payload.content,
            context_payload={
                "chat_id": str(payload.chat_id),
                "sender_id": payload.sender_id,
                "source": "feishu",
            },
        )

        # 5. 获取 Agent 响应
        if result.is_success and result.output:
            response_text = result.output
        else:
            response_text = "抱歉，处理您的请求时出现问题，请稍后重试。"

        # 6. 根据聊天类型路由回复
        response_content = self._format_response(response_text)

        if payload.chat_type == ChatType.P2P:
            reply_id = await self.feishu_client.send_message(
                chat_id=payload.chat_id,
                content=response_content,
            )
        else:
            reply_id = await self.feishu_client.reply_message(
                message_id=payload.message_id,
                content=response_content,
            )

        # 7. 更新会话上下文
        context.set_session(result.session_id)
        await self.context_repo.save(context)

        return HandleFeishuMessageResult(
            reply_message_id=reply_id,
            session_id=result.session_id,
        )

    def _build_system_prompt(self, context) -> str:
        """构建包含对话历史的 system prompt"""
        history_lines = []
        for msg in context.messages:
            role = "用户" if msg["role"] == "user" else "助手"
            history_lines.append(f"{role}: {msg['content']}")

        history = "\n".join(history_lines) if history_lines else "无历史对话"

        return f"""你是一个智能助手，通过飞书即时通讯平台与用户交流。

## 对话历史
{history}

## 指导原则
- 友好、专业地回应用户
- 保持回复简洁明了
- 如果需要执行代码或文件操作，明确说明你在做什么
"""

    def _format_response(self, text: str) -> str:
        """格式化飞书消息内容"""
        return json.dumps({"text": text}, ensure_ascii=False)