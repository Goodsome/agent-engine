from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Dependency

from agent_engine.integration.application.use_cases.handle_feishu_message import (
    HandleFeishuMessage,
)
from agent_engine.integration.infrastructure.adapters.lark_ws_client import LarkWsClient
from agent_engine.integration.infrastructure.adapters.sql_alchemy_conversation_context_repository import (
    SqlAlchemyConversationContextRepository,
)


class Container(DeclarativeContainer):
    """Integration 限界上下文容器"""

    config: Configuration = Configuration()
    session_factory = Dependency()
    execute_session = Dependency()

    # Feishu 客户端适配器
    lark_ws_client: Factory[LarkWsClient] = Factory(
        LarkWsClient,
        app_id=config.FEISHU_APP_ID,
        app_secret=config.FEISHU_APP_SECRET,
    )

    # 会话上下文仓储
    sql_alchemy_conversation_context_repository: Factory[SqlAlchemyConversationContextRepository] = Factory(
        SqlAlchemyConversationContextRepository,
        session_factory=session_factory,
    )

    # 用例: 处理飞书消息
    handle_feishu_message: Factory[HandleFeishuMessage] = Factory(
        HandleFeishuMessage,
        feishu_client=lark_ws_client,
        execute_session=execute_session,
        context_repo=sql_alchemy_conversation_context_repository,
    )