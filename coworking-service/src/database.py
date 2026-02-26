from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_engine = None
_session_factory = None


def _init():
    global _engine, _session_factory
    if _engine is not None:
        return
    from src.config import database_settings

    _engine = create_async_engine(
        database_settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


def get_engine():
    _init()
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    _init()
    assert _session_factory is not None
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
