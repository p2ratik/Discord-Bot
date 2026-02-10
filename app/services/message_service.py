from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.schemas.chat import Payload
from app.schemas.chat import BotMessageRecieve as bMp
from app.schemas.chat import ChannelMessages
from app.models.message import BotMessages
from typing import Optional

async def get_user_messages(user_id : str, db:AsyncSession)->Optional[BotMessages]:
    # To get the top 10 messages if exist
    try:
        results = await db.execute(select(BotMessages).where(BotMessages.user_id == user_id).order_by(desc(BotMessages.id)).limit(5))
        messages = results.scalars().all()
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in getting messages {e}")

async def add_user_messages(message: bMp, db:AsyncSession):
    # Storing the current message in the database

    try:
       db_message = BotMessages(**message.model_dump()) 
       db.add(db_message)

       await db.commit()
       await db.refresh(db_message)
       print(f"Message {message.user_id} , {message.content} added to the database")

    except Exception as e:
        await db.rollback()
        print(f"Error occured {e}")

async def get_all_messages(message : ChannelMessages, db:AsyncSession):
    # Storing all messages
    pass