from os import error
import asyncio
from math import exp
from sqlalchemy import text
from typing import AsyncGenerator
from app.core.config import settings
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel.ext.asyncio.session import AsyncSession
from app.core.loguru_logging import get_logger, LoggerType
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

logger: LoggerType = get_logger()


engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)


async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        if session:
            try:
                await session.rollback()
                logger.info("Successfully rolled back session after error")
            except Exception as rollback_error:
                logger.error(f"Error during session rollback: {rollback_error}")
        raise
    finally:
        if session:
            try:
                await session.close()
                logger.debug("Database session closed successfully")
            except Exception as close_error:
                logger.error(f"Error closing database session: {close_error}")


async def init_db() -> None:
    try:
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                async with engine.begin() as conn:
                    await conn.excute(text("SELECT 1"))
                logger.info("Database connection verified successfully")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(
                        f"Failed to verify database connection after {max_retries} attempts"
                    )
                    raise
                logger.warning(f"Database connection attempt {attempt+1}")
                await asyncio.sleep(retry_delay * (attempt + 1))
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
