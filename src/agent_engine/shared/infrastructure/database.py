from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def create_db_engine(db_url: str):
    """
    初始化共享的数据库引擎
    使用 SQLAlchemy 2.0 异步风格，结合 asyncpg 或 psycopg
    """
    # 如果配置的是 postgresql://，自动转换为异步的 postgresql+psycopg://
    if db_url and db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return create_async_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # 充分利用 PostgreSQL 的连接池健康检查
        echo=False,
    )


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    """
    创建异步会话工厂
    """
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
