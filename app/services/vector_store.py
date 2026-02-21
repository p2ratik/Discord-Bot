from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatVector
from app.schemas.whatsapp_info import Chatmodel
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def insert_vectors(chats, db: AsyncSession):
    """Insert embedded chat pairs into the database in a single transaction."""

    for chat in chats['pairs']:
        chat_vector = Chatmodel(
            user_id=chats['sender_id'],
            incoming=chat['incoming'],
            reply=chat['reply'],
            embedding=chat['embedding'],
        )

        db_vector = ChatVector(**chat_vector.model_dump())
        db.add(db_vector)

    try:
        await db.commit()
        logger.info(f"Successfully inserted {len(chats['pairs'])} vectors into the database")
    except Exception as e:
        logger.error(f"❌ Failed to insert vectors: {e}")
        await db.rollback()
        raise RuntimeError(f"Database insert failed: {e}")
