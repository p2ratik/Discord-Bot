from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import Payload
from app.services.chat_service import process_chat
from app.db.session import get_db
from app.utils.logger import get_logger
import time

logger = get_logger(__name__)

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
    start_time = time.time()
    logger.info(f"[API] Chat request from user {payload.user_id} in channel {payload.channel_id}")
    
    try:
        result = await process_chat(payload, db)
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"[API] Chat request completed in {elapsed:.2f}ms")
        return result
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(f"[API] Chat request failed after {elapsed:.2f}ms: {e}", exc_info=True)
        raise

