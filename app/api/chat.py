from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import Payload
from app.services.chat_service import process_chat
from app.db.session import get_db

router = APIRouter()


@router.post('/chat')
async def chat_endpoint(payload: Payload, db: AsyncSession = Depends(get_db)) -> dict:
    """
    Handle chat messages and return responses
    
    :param payload: Chat message payload
    :type payload: Payload
    :param db: Database session
    :type db: AsyncSession
    :return: Dictionary with reply
    """
    print(f"Received message from {payload.user_id}: {payload.content}")
    return await process_chat(payload, db)

