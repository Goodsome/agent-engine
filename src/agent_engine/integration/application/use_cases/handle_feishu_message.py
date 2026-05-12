import json
from dataclasses import dataclass
from agent_engine.integration.domain.aggregates.conversation_context import (
    ConversationContext,
)
from agent_engine.integration.domain.ports.conversation_context_repository import (
    ConversationContextRepository,
)
from agent_engine.dispatching.application.use_cases.execute_session import ExecuteSession
from agent_engine.dispatching.application.dtos.execute_session_command import ExecuteSessionCommand
from agent_engine.dispatching.domain.enums import DispatchStatus
from agent_engine.shared.domain.value_objects.session_id import SessionId
from agent_engine.integration.domain.ports.feishu_client_port import FeishuClientPort
from agent_engine.integration.application.dtos.handle_feishu_message_command import HandleFeishuMessageCommand
from agent_engine.integration.application.dtos.handle_feishu_message_result import HandleFeishuMessageResult
from agent_engine.integration.domain.enums import ChatType


@dataclass
class HandleFeishuMessage:
    """处理飞书消息 - 非流式响应

    流程:
    1. 获取或创建会话上下文
    2. 触发 Agent 执行 (直接调用 Dispatching 域)
    3. 根据聊天类型路由回复 (P2P 发送新消息, GROUP 回复消息)
    4. 更新会话上下文
    """

    feishu_client: FeishuClientPort
    execute_session: ExecuteSession
    context_repo: ConversationContextRepository

    async def execute(self, cmd: HandleFeishuMessageCommand) -> HandleFeishuMessageResult:
        payload = cmd.payload

        # 1. 获取或创建会话上下文
        context = await self.context_repo.find_by_chat_id(payload.chat_id)
        if context is None:
            context = ConversationContext.create(payload.chat_id)

        # 添加用户消息到历史
        context.add_message("user", payload.content)

        # 2. 构建 system prompt (包含对话历史)
        system_prompt = self._build_system_prompt(context)

        # 3. 准备 SessionId
        # 如果当前上下文已有 session_id 则沿用，否则新建
        session_id = context.current_session_id or SessionId.create()

        # 4. 触发 Agent 执行
        execute_cmd = ExecuteSessionCommand(
            system_prompt=system_prompt,
            user_prompt=payload.content,
            session_id=str(session_id.value),
            context_payload={
                "chat_id": str(payload.chat_id),
                "sender_id": payload.sender_id,
                "source": "feishu",
            },
        )
        result = await self.execute_session.execute(execute_cmd)

        # 5. 获取 Agent 响应
        if result.status == DispatchStatus.SUCCESS and result.output:
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
        context.set_session(session_id)
        await self.context_repo.save(context)

        return HandleFeishuMessageResult(
            reply_message_id=reply_id,
            session_id=session_id,
        )

    def _build_system_prompt(self, context: ConversationContext) -> str:
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