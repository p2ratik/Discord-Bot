from sqlalchemy import Column, Integer, String, DateTime
from app.db.base import Base


class ChannelMessages(Base):
    """ORM model for channel_messages table"""
    __tablename__ = "channel_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(String(32))
    channel_id = Column(String(32))
    user_id = Column(String(50))
    content = Column(String(300))
    dateTime = Column(DateTime)


class BotMessages(Base):
    """ORM model for bot_messages table"""
    __tablename__ = "bot_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(32))
    user_id = Column(String(50))
    content = Column(String(300))
    dateTime = Column(DateTime)
