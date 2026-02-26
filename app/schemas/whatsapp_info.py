from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import numpy as np

class Chatmodel(BaseModel):
    """
    Vector Embeddings
    """
    user_id:str     
    incoming:str
    reply:str    
    embedding :List[float]

class Reciever(BaseModel):
    """Data Recieved from the frontend"""
    sender_name:str
    reciever_name:str
    sender_id:str
    reciever_id:str

