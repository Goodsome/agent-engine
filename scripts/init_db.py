import asyncio
import sys
import logging
from urllib.parse import urlparse, urlunparse

from sqlalchemy import text, create_engine
from sqlalchemy.exc import OperationalError

from agent_engine.config import get_settings
from agent_engine.shared.infrastructure.database import Base, create_db_engine

# 如果有定义好的 SQLAlchemy 模型，请在这里导入它们，以便 Base 能够识别到
# 例如：
# from agent_engine.execution.infrastructure.repositories.models import ...
# from agent_engine.orchestration.infrastructure.repositories.models import ...

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_init")


def create_database_if_not_exists(url: str):
    """如果目标数据库不存在，则创建它 (使用同步引擎执行管理员任务)"""
    parsed = urlparse(url)
    db_name = parsed.path.lstrip('/')
    
    if not db_name:
        logger.error("No database name found in the URL.")
        return

    # 切换到 psycopg 驱动，并连接到 'postgres' 默认库执行管理员任务
    scheme = "postgresql+psycopg" if parsed.scheme == "postgresql" else parsed.scheme
    admin_url = urlunparse(parsed._replace(scheme=scheme, path='/postgres'))
    
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    
    try:
        with engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            exists = result.scalar()
            
            if not exists:
                logger.info(f"Database '{db_name}' does not exist. Creating...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully.")
            else:
                logger.info(f"Database '{db_name}' already exists.")
    except Exception as e:
        logger.error(f"Failed to check/create database: {e}")
        # 如果无法连接到 postgres 管理库，可能当前用户没权限，但不影响目标库已经存在的情况
    finally:
        engine.dispose()


async def init_db_tables(db_url: str):
    """使用异步引擎创建数据库表结构"""
    engine = create_db_engine(db_url)
    try:
        async with engine.begin() as conn:
            # 运行同步的 create_all 建立所有继承自 Base 的表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully.")
    except OperationalError as e:
        logger.error(f"Connection failed while creating tables: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
    finally:
        await engine.dispose()


async def main_async():
    settings = get_settings()
    
    if not settings.DATABASE_URL:
        logger.warning("DATABASE_URL is not set. Skipping real DB initialization.")
        sys.exit(0)
        
    db_url = str(settings.DATABASE_URL)
    
    # 隐藏日志中的密码
    parsed = urlparse(db_url)
    safe_netloc = f"{parsed.username}:***@{parsed.hostname}:{parsed.port}" if parsed.username else parsed.hostname
    safe_url = urlunparse(parsed._replace(netloc=safe_netloc))
    logger.info(f"Initializing database at {safe_url}")
    
    try:
        # 如果是 PostgreSQL，则先检查并创建数据库
        if parsed.scheme.startswith("postgresql"):
            create_database_if_not_exists(db_url)
            
        # 初始化表结构 (依赖于你在上方导入的模型类)
        await init_db_tables(db_url)
        logger.info("Database initialization completed successfully.")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
