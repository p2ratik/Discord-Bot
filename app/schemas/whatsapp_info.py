from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Reciever(BaseModel):
    sender_name:str
    reciever_name:str
    sender_id:str
    reciever_id:str
    