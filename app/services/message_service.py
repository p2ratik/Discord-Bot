from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.schemas.chat import Payload
from app.schemas.chat import BotMessageRecieve as bMp
from app.schemas.chat import ChannelMessages
from app.models.message import BotMessages
from app.utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

async def get_user_messages(user_id : str, db:AsyncSession)->Optional[BotMessages]:
    """Get the last 5 messages for a user"""
    try:
        logger.debug(f"Fetching last 5 messages for user: {user_id}")
        results = await db.execute(select(BotMessages).where(BotMessages.user_id == user_id).order_by(desc(BotMessages.id)).limit(5))
        messages = results.scalars().all()
        logger.debug(f"Retrieved {len(messages)} messages for user {user_id}")
        return messages
    except Exception as e:
        logger.error(f"Error fetching messages for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error in getting messages {e}")

async def add_user_messages(message: bMp, db:AsyncSession):
    """Store a message in the database"""
    try:
       logger.debug(f"Storing message for user {message.user_id} in channel {message.channel_id}")
       db_message = BotMessages(**message.model_dump()) 
       db.add(db_message)

       await db.commit()
       await db.refresh(db_message)
       logger.info(f"Successfully stored message for user {message.user_id}")

    except Exception as e:
        await db.rollback()
        logger.error(f"Error storing message for user {message.user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error storing message: {e}")

async def get_all_messages(message : ChannelMessages, db:AsyncSession):
    # Storing all messages
    pass