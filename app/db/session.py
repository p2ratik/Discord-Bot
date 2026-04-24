import os
from urllib.parse import urlparse
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


def _should_enable_ssl(url: str | None) -> bool:
    """Enable SSL based on DB_SSL env or URL host heuristics."""
    db_ssl = os.getenv("DB_SSL", "auto").strip().lower()

    if db_ssl in {"1", "true", "yes", "on", "require"}:
        return True
    if db_ssl in {"0", "false", "no", "off", "disable"}:
        return False

    if not url:
        return False

    host = (urlparse(url).hostname or "").lower()
    local_hosts = {"localhost", "127.0.0.1", "postgres", "db"}
    return host not in local_hosts


engine_kwargs = {
    "echo": False,
    "pool_size": 10,
    "max_overflow": 20,
}

if _should_enable_ssl(db_url):
    engine_kwargs["connect_args"] = {"ssl": True}

engine = create_async_engine(
    db_url,
    **engine_kwargs,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
