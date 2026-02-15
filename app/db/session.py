import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.db.base import Base

load_dotenv()
password = os.getenv('POSTGRES_PASSWORD')

db_url = os.getenv('DATABASE_URL')

engine = create_async_engine(
    db_url,
    echo=False,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
