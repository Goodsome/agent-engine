import json
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Callable, Awaitable

import lark_oapi as lark
from lark_oapi.api.im.v1 import (
    CreateMessageRequest,
    CreateMessageRequestBody,
    ReplyMessageRequest,
    ReplyMessageRequestBody,
    P2ImMessageReceiveV1,
)

from agent_engine.integration.domain.ports.feishu_client_port import FeishuClientPort
from agent_engine.integration.domain.value_objects.chat_id import ChatId
from agent_engine.integration.domain.value_objects.feishu_message_id import (
    FeishuMessageId,
)
from agent_engine.integration.domain.value_objects.feishu_message_payload import (
    FeishuMessagePayload,
)
from agent_engine.integration.domain.enums import ChatType


@dataclass
class LarkWsClient(FeishuClientPort):
    """基于 lark-oapi SDK 的 WebSocket 客户端实现

    支持两种消息处理模式:
    1. P2P 私聊: 通过 chat_id 创建新消息
    2. GROUP 群聊: 通过 message_id 回复消息

    注意: lark-oapi 的 WebSocket 客户端是同步的，start() 方法内部调用
    loop.run_until_complete()，因此在 asyncio.run() 环境下需要通过
    run_in_executor 在线程池中运行。
    """

    app_id: str
    app_secret: str
    _client: lark.Client = field(default=None, init=False)
    _ws_client: lark.ws.Client = field(default=None, init=False)
    _message_handler: Callable[[FeishuMessagePayload], Awaitable[None]] | None = field(
        default=None, init=False
    )
    _loop: asyncio.AbstractEventLoop | None = field(default=None, init=False)

    def __post_init__(self):
        """初始化 Lark 客户端"""
        self._client = (
            lark.Client.builder()
            .app_id(self.app_id)
            .app_secret(self.app_secret)
            .build()
        )

    async def send_message(self, chat_id: ChatId, content: str) -> FeishuMessageId:
        """发送新消息到会话 (P2P 私聊)

        Args:
            chat_id: 会话ID
            content: JSON 格式的消息内容

        Returns:
            发送的消息ID
        """
        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(str(chat_id))
                .msg_type("text")
                .content(content)
                .build()
            )
            .build()
        )

        # lark-oapi SDK 是同步的，需要在executor中运行
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, self._client.im.v1.message.create, request
        )

        if not response.success():
            raise Exception(
                f"send_message failed, code: {response.code}, msg: {response.msg}"
            )

        return FeishuMessageId.create(response.data.message_id)

    async def reply_message(
        self, message_id: FeishuMessageId, content: str
    ) -> FeishuMessageId:
        """回复消息 (群聊)

        Args:
            message_id: 要回复的消息ID
            content: JSON 格式的回复内容

        Returns:
            回复的消息ID
        """
        request = (
            ReplyMessageRequest.builder()
            .message_id(str(message_id))
            .request_body(
                ReplyMessageRequestBody.builder()
                .content(content)
                .msg_type("text")
                .build()
            )
            .build()
        )

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None, self._client.im.v1.message.reply, request
        )

        if not response.success():
            raise Exception(
                f"reply_message failed, code: {response.code}, msg: {response.msg}"
            )

        return FeishuMessageId.create(response.data.message_id)

    async def update_message(self, message_id: FeishuMessageId, content: str) -> None:
        """更新消息内容 (用于流式输出)

        注意: 飞书消息更新有频率限制，需要合理控制更新频率

        Args:
            message_id: 要更新的消息ID
            content: 新的消息内容
        """
        # TODO: 实现 PatchMessage API 调用
        # 飞书 PatchMessage API 需要处理版本控制和并发冲突
        raise NotImplementedError("Stream update not implemented in Phase 1")

    def set_message_handler(
        self, handler: Callable[[FeishuMessagePayload], Awaitable[None]]
    ) -> None:
        """设置消息处理器

        Args:
            handler: 异步消息处理函数
        """
        self._message_handler = handler

    async def start_listener(self) -> None:
        """启动 WebSocket 监听器

        监听飞书消息事件，解析后调用消息处理器

        Note: lark-oapi 的 ws_client.start() 是同步方法，内部会创建自己的事件循环。
        因此需要在线程池中运行，避免与 asyncio.run() 冲突。
        """
        self._loop = asyncio.get_running_loop()

        def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
            """处理接收到的消息事件

            此回调在 Lark SDK 的内部线程中执行，需要通过
            run_coroutine_threadsafe 安全地调度异步任务到主事件循环。
            """
            try:
                if self._message_handler is None or self._loop is None:
                    return

                # 解析消息内容
                content = ""
                if data.event.message.message_type == "text":
                    content = json.loads(data.event.message.content).get("text", "")
                else:
                    content = "暂不支持此类型消息"

                # 确定聊天类型
                chat_type = (
                    ChatType.P2P
                    if data.event.message.chat_type == "p2p"
                    else ChatType.GROUP
                )

                # 构建消息负载
                payload = FeishuMessagePayload(
                    message_id=FeishuMessageId.create(data.event.message.message_id),
                    chat_id=ChatId.create(data.event.message.chat_id),
                    chat_type=chat_type,
                    content=content,
                    sender_id=data.event.sender.sender_id.user_id,
                )

                # 使用 run_coroutine_threadsafe 安全地调度异步任务
                # 这是从同步回调跨线程调用异步函数的标准模式
                asyncio.run_coroutine_threadsafe(
                    self._message_handler(payload), self._loop
                )
            except Exception as e:
                # 捕获异常以防止 WebSocket 客户端崩溃
                logging.getLogger(__name__).exception(
                    "处理飞书消息失败: %s", e
                )

        # 创建事件处理器
        event_handler = (
            lark.EventDispatcherHandler.builder("", "")
            .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
            .build()
        )

        # 创建 WebSocket 客户端
        self._ws_client = lark.ws.Client(
            self.app_id,
            self.app_secret,
            event_handler=event_handler,
            log_level=lark.LogLevel.INFO,
        )

        # 在线程池中运行同步的 WebSocket 客户端
        # 避免与 asyncio.run() 创建的事件循环冲突
        await self._loop.run_in_executor(None, self._ws_client.start)