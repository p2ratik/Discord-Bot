from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base


class Role(Base):
    """ORM model for role table"""
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True)
    user_name = Column(String(32))
    role = Column(JSONB)

