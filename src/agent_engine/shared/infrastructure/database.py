from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase
import logging


class Base(DeclarativeBase):
    pass


class Database:
    """
    Async database connection handling using SQLAlchemy.
    """
    def __init__(self, connection_string: str) -> None:
        # 如果配置的是 postgresql://，自动转换为异步的 postgresql+psycopg://
        if connection_string and connection_string.startswith("postgresql://"):
            connection_string = connection_string.replace("postgresql://", "postgresql+psycopg://", 1)

        self._engine: AsyncEngine = create_async_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # 充分利用 PostgreSQL 的连接池健康检查
            echo=False,
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def get_session(self) -> AsyncSession:
        """Create a new async database session."""
        return self._session_factory()

    async def close(self) -> None:
        """Close the database connection pool."""
        await self._engine.dispose()

    async def init_db(self) -> None:
        """Create database tables if they don't exist."""
        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logging.info("Database tables created successfully.")
        except Exception as e:
            logging.error(f"Failed to create database tables: {e}")
            raise e

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    @property
    def engine(self) -> AsyncEngine:
        """Get the underlying SQLAlchemy async engine."""
        return self._engine


async def init_database(connection_string: str) -> AsyncIterator[Database]:
    """数据库资源的生命周期管理"""
    # 1. 实例化 Database 对象
    db = Database(connection_string)

    # 2. 启动时的初始化逻辑 (对应 init_resources)
    try:
        # 显式连一下数据库测试连通性，做到 Fail-Fast
        async with db.engine.connect() as _:
            pass

        # 建表逻辑
        await db.init_db()
        logging.info("Database initialized and connected successfully.")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        raise e

    # 3. 将准备就绪的数据库实例 yield 给容器
    yield db

    # 4. 关闭时的清理逻辑 (对应 shutdown_resources)
    logging.info("Closing database connection pool...")
    await db.close()
