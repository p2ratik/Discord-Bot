from sqlalchemy import Column, Integer, String, JSON
from app.db.base import Base


class Role(Base):
    """ORM model for role table"""
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True)
    user_name = Column(String(32))
    role = Column(JSON)

#JSON Format : {"role":['girlfriend'] "nicknames":['babe', 'honey', 'princess', 'bhondhu'] "nature":["introvert", "loves maths", "plays Roblox"] , "additional_info":["likes to eat chowmine", "hates spiders"]}