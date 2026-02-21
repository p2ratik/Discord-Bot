from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    s3_key: str
    job_id: str
