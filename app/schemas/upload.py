from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    message:str
    s3_key:str
