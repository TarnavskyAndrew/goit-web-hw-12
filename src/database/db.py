from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
import contextlib
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.conf.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True)
SessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


@contextlib.asynccontextmanager
async def session():
    async with SessionLocal() as s:
        try:
            yield s
        except:
            await s.rollback()
            raise
        finally:
            await s.close()


async def get_db():
    async with session() as s:
        yield s
