from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.db.base import Base

class Admin(Base):
    """ORM model for admin table"""
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), index=True)
    role = Column(JSON)