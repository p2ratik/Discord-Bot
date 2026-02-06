from pydantic import BaseModel
from datetime import datetime
from typing import Any


class Payload(BaseModel):
    """Pydantic schema for chat payload"""
    user_id: str
    server_id: str
    channel_id: str
    content: str


class ChannelMessages(BaseModel):
    """Pydantic schema for ChannelMessages"""
    id: int
    server_id: Any
    channel_id: Any
    user_id: str
    content: str
    dateTime: datetime


class BotMessages(BaseModel):
    """Pydantic schema for BotMessages"""
    id: int
    channel_id: Any
    user_id: str
    content: str
    dateTime: datetime
    bot_reply:str

class BotMessageRecieve(BaseModel):
    user_id : str
    channel_id:Any
    content:str
    bot_reply:str