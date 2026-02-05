"""
Database initialization script
Run this to create all tables in the database
"""
import asyncio
from app.db.base import Base
from app.db.session import engine

# Import all models so they're registered with Base
from app.models.user import User
from app.models.role import Role
from app.models.message import ChannelMessages, BotMessages


async def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    
    async with engine.begin() as conn:
        # Drop all tables (optional - comment out if you want to keep existing data)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    print("\nCreated tables:")
    print("  - users")
    print("  - role")
    print("  - channel_messages")
    print("  - bot_messages")


if __name__ == "__main__":
    asyncio.run(init_db())
