from math import exp
from typing import AsyncGenerator
from app.core.config import settings
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.loguru_logging import get_logger, LoggerType
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

logger: LoggerType = get_logger()


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL)


async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    pass
