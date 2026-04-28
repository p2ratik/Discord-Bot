from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.roles import router as roles_router
from app.api.users import router as users_router
from app.api.chat_upload import router as upload_router
from app.api.admin_roles import router as admin_router
from app.api.jobs import router as jobs_router
from app.db.base import Base
from app.discord_bot.bot import run_bot
from app.db.session import engine
from app.utils.logger import get_logger
import asyncio
import os

logger = get_logger(__name__)

app = FastAPI(title="Discord Bot API")

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(admin_router)
app.include_router(upload_router)
app.include_router(jobs_router)


@app.get("/")
def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Discord Bot API is running", "version": "1.0.0"}

@app.get("/health")
def health():
    "Health Endpoint"
    logger.info("Health endpoint accessed")
    return {"health": "OK bot running fine "}

@app.on_event("startup")
async def startup():
    """Create database tables on startup"""
    logger.info("Application starting up...")
    max_retries = int(os.getenv("DB_STARTUP_RETRIES", "5"))
    retry_delay = float(os.getenv("DB_STARTUP_RETRY_DELAY", "2"))

    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified successfully")
            logger.info("Discord Bot API is ready to accept requests")
            break
        except Exception as e:
            if attempt == max_retries:
                logger.error(
                    "Failed to initialize database after %s attempts: %s",
                    max_retries,
                    e,
                    exc_info=True,
                )
                raise

            sleep_for = retry_delay * attempt
            logger.warning(
                "Database startup attempt %s/%s failed (%s). Retrying in %.1f seconds...",
                attempt,
                max_retries,
                e,
                sleep_for,
            )
            await asyncio.sleep(sleep_for)

    # Launch the Discord bot as a background task so it doesn't block the server
    asyncio.create_task(run_bot())
    logger.info("Discord bot launched in background")
