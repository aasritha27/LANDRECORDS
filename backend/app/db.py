from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os
from app.config import settings

# Flexible Database Engine Setup (Fallback to local SQLite if Postgres is unavailable)
db_url = settings.DATABASE_URL
sync_db_url = settings.SYNC_DATABASE_URL

# Default fallback to SQLite for local lightweight execution
if "postgresql" in db_url:
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        # Check if Postgres port 5432 is open
        result = s.connect_ex(('localhost', 5432))
        s.close()
        if result != 0:
            # Port 5432 not open -> fallback to SQLite
            db_url = "sqlite+aiosqlite:///./land_records.db"
            sync_db_url = "sqlite:///./land_records.db"
    except Exception:
        db_url = "sqlite+aiosqlite:///./land_records.db"
        sync_db_url = "sqlite:///./land_records.db"

engine = create_async_engine(
    db_url,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

sync_engine = create_engine(sync_db_url, echo=False)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
