import asyncio
import json
import psycopg
from datetime import datetime

# 数据库连接配置
# 格式: postgresql://user:password@host:port/dbname
DB_DSN = "postgresql://postgres:postgres@localhost:5432/task_graph"
CHANNEL_NAME = "task_events"

async def event_handler(payload: str):
    """处理接收到的事件数据"""
    try:
        data = json.loads(payload)
        event_type = data.get("event_type", "UnknownEvent")
        occurred_at = data.get("occurred_at", "UnknownTime")
        
        print(f"\n{"="*40}")
        print(f"🔔 收到事件: {event_type}")
        print(f"⏰ 发生时间: {occurred_at}")
        print(f"📦 完整载荷: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"{"="*40}")
        
        # 这里未来可以根据 event_type 路由到不同的处理逻辑
        if event_type == "TaskReadyEvent":
            print(f"🚀 动作: 准备拉起任务 {data.get('task_id')} 的执行器...")
            
    except Exception as e:
        print(f"❌ 解析事件失败: {e}")

async def listen_for_events():
    """监听 PostgreSQL NOTIFY 的主循环"""
    try:
        # 使用 autocommit=True，因为 LISTEN 命令不需要开启事务
        async with await psycopg.AsyncConnection.connect(DB_DSN, autocommit=True) as conn:
            print(f"✅ 已连接到数据库，正在监听频道: '{CHANNEL_NAME}'...")
            
            # 执行 LISTEN 指令
            await conn.execute(f"LISTEN {CHANNEL_NAME}")
            
            # psycopg3 极其优雅的异步生成器接口
            # 它会自动处理底层的轮询，并在有消息时唤醒
            async for notify in conn.notifies():
                await event_handler(notify.payload)
                
    except psycopg.OperationalError as e:
        print(f"💥 数据库连接错误: {e}")
    except asyncio.CancelledError:
        print("🛑 监听已停止")

if __name__ == "__main__":
    try:
        asyncio.run(listen_for_events())
    except KeyboardInterrupt:
        pass