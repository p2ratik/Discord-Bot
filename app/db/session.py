import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.db.base import Base

load_dotenv()

db_url = os.getenv('DATABASE_URL')

# Render/Heroku provide DATABASE_URL as "postgresql://..." or "postgres://..."
# which defaults to the sync psycopg2 driver. SQLAlchemy's async engine
# requires "postgresql+asyncpg://...", so we rewrite the scheme.
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

#new add: Heroku's DATABASE_URL may include sslmode=require, which asyncpg doesn't support. We remove it.
if db_url and "sslmode" in db_url:
    db_url = db_url.split("?")[0]        

engine = create_async_engine(
    db_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
    connect_args={"ssl": True} #newnew
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
