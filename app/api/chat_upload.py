from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.schemas.upload import UploadResponse
from app.utils.logger import get_logger
from app.redis.queue import task_queue
from app.services.pipeline import run_pipeline_sync
from app.aws.aws_service import upload_file_to_s3
from rq import Retry
import uuid

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chats"])


@router.post("/upload-chat", response_model=UploadResponse, status_code=201)
async def upload_chat(
    file: UploadFile = File(...),
    sender_name: str = Form(...),
    reciever_name: str = Form(...),
    sender_id: str = Form(...),
    reciever_id: str = Form(...),
):
    """
    Accept a WhatsApp chat .txt export along with sender/reciever info,
    upload the file to S3, and enqueue the processing pipeline.
    """

    # Validate file type
    if not file.filename or not file.filename.endswith(".txt"):
        logger.warning("File not uploaded. Wrong file format or missing filename")
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    uid = str(uuid.uuid4())
    s3_key = f"raw/{uid}_{file.filename}"

    logger.info(f"Generated S3 key: {s3_key}")

    try:
        await upload_file_to_s3(file.file, s3_key)
        logger.info("File uploaded to S3 successfully")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"S3 upload error: {e}")

    reciever_data = {
        "sender_name": sender_name,
        "reciever_name": reciever_name,
        "sender_id": sender_id,
        "reciever_id": reciever_id,
    }

    # Enqueue the pipeline job
    job = task_queue.enqueue(
        run_pipeline_sync,
        uid,
        s3_key,
        reciever_data,
        job_timeout="10m",
        result_ttl=3600,
        retry=Retry(max=2, interval=30),
    )

    logger.info(f"Pipeline job enqueued: {job.id}")

    return UploadResponse(
        message="File uploaded — processing queued",
        s3_key=s3_key,
        job_id=job.id,
    )