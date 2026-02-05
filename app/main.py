from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.roles import router as roles_router
from app.api.users import router as users_router
from app.db.base import Base
from app.db.session import engine

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


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Discord Bot API is running", "version": "1.0.0"}


@app.on_event("startup")
async def startup():
    """Create database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

