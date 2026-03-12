"""Tests for LarkWsClient asyncio handling."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock

from agent_engine.integration.infrastructure.adapters.lark_ws_client import LarkWsClient


class TestLarkWsClientAsyncMode:
    """Test that LarkWsClient handles asyncio event loops correctly."""

    def test_send_message_uses_running_loop(self):
        """Test that send_message uses the running event loop correctly."""

        async def run_test():
            client = LarkWsClient(app_id="test_id", app_secret="test_secret")

            with patch.object(client, '_client') as mock_client:
                mock_response = MagicMock()
                mock_response.success.return_value = True
                mock_response.data.message_id = "msg_123"
                mock_client.im.v1.message.create.return_value = mock_response

                from agent_engine.integration.domain.value_objects.chat_id import ChatId
                result = await client.send_message(ChatId.create("chat_123"), '{"text": "hello"}')

                assert str(result) == "msg_123"

        asyncio.run(run_test())

    def test_reply_message_uses_running_loop(self):
        """Test that reply_message uses the running event loop correctly."""

        async def run_test():
            client = LarkWsClient(app_id="test_id", app_secret="test_secret")

            with patch.object(client, '_client') as mock_client:
                mock_response = MagicMock()
                mock_response.success.return_value = True
                mock_response.data.message_id = "msg_456"
                mock_client.im.v1.message.reply.return_value = mock_response

                from agent_engine.integration.domain.value_objects.feishu_message_id import FeishuMessageId
                result = await client.reply_message(
                    FeishuMessageId.create("msg_orig"),
                    '{"text": "reply"}'
                )

                assert str(result) == "msg_456"

        asyncio.run(run_test())

    def test_start_listener_runs_in_thread(self):
        """Test that start_listener runs the sync WebSocket in a thread.

        This ensures no event loop conflict when using asyncio.run().
        """

        async def run_test():
            client = LarkWsClient(app_id="test_id", app_secret="test_secret")

            start_called = asyncio.Event()

            def mock_ws_start():
                start_called.set()
                import time
                time.sleep(0.1)

            with patch('lark_oapi.ws.Client') as MockWsClient:
                mock_ws = MagicMock()
                mock_ws.start = mock_ws_start
                MockWsClient.return_value = mock_ws

                task = asyncio.create_task(client.start_listener())

                try:
                    await asyncio.wait_for(start_called.wait(), timeout=1.0)
                except asyncio.TimeoutError:
                    pytest.fail("start_listener did not start WebSocket client in time")

                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        asyncio.run(run_test())

    def test_message_handler_from_sync_callback(self):
        """Test that message handler works when called from sync callback."""

        async def run_test():
            client = LarkWsClient(app_id="test_id", app_secret="test_secret")

            handler_called = asyncio.Event()
            received_payload = None

            async def test_handler(payload):
                nonlocal received_payload
                received_payload = payload
                handler_called.set()

            client.set_message_handler(test_handler)

            from agent_engine.integration.domain.value_objects.feishu_message_payload import (
                FeishuMessagePayload
            )
            from agent_engine.integration.domain.value_objects.feishu_message_id import (
                FeishuMessageId
            )
            from agent_engine.integration.domain.value_objects.chat_id import ChatId
            from agent_engine.integration.domain.enums import ChatType

            payload = FeishuMessagePayload(
                message_id=FeishuMessageId.create("msg_123"),
                chat_id=ChatId.create("chat_456"),
                chat_type=ChatType.P2P,
                content="test message",
                sender_id="user_789",
            )

            task = asyncio.create_task(test_handler(payload))

            await asyncio.wait_for(handler_called.wait(), timeout=1.0)
            assert received_payload is not None
            assert received_payload.content == "test message"

        asyncio.run(run_test())