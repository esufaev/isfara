# --- START OF FILE database.py ---
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+asyncpg://admin:12345@localhost:5432/isfara_db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Зависимость для получения сессии БД в роутах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
# --- END OF FILE database.py ---
