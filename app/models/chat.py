from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector
from app.db.base import Base

class ChatVector(Base):
    __tablename__ = "chat_vectors"

    id = Column(Integer, primary_key=True)
    user_id = Column(Text)     
    incoming = Column(Text)    
    reply = Column(Text)       
    embedding = Column(Vector(384))

