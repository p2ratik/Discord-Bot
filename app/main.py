from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.roles import router as roles_router
from app.api.users import router as users_router
from app.api.admin_roles import router as admin_router
from app.db.base import Base
from app.db.session import engine
from app.utils.logger import get_logger

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
app.include_router(roles_router)
app.include_router(users_router)
app.include_router(admin_router)


@app.get("/")
def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Discord Bot API is running", "version": "1.0.0"}


@app.on_event("startup")
async def startup():
    """Create database tables on startup"""
    logger.info("Application starting up...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified successfully")
        logger.info("Discord Bot API is ready to accept requests")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise

