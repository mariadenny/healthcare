from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import Settings, get_settings

settings: Settings = get_settings()

# Use async SQLite for dev fallback; assume DATABASE_URL is async URL (e.g., sqlite+aiosqlite:///./test.db or postgresql+asyncpg://...)
engine = create_async_engine(settings.database_url, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Dependency for FastAPI routes
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
