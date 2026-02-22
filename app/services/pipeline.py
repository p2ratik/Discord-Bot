# Main data pipeline
# Connected with Redis Queue and Worker

import tempfile
import os
import json
import asyncio
from app.aws.aws_service import download_file_from_s3, upload_file_to_s3
from app.services.parse_whatsapp_chats import parse_whatsapp_chat
from app.schemas.whatsapp_info import Reciever
from app.services.vector_store import insert_vectors
from app.services.embeddings import embed_pairs
from app.db.session import AsyncSessionLocal
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def process_chat_pipeline(job_id: str, s3_key: str, reciever_data: dict):
    """
    Full async pipeline:
      1. Download chat export from S3
      2. Parse WhatsApp messages into pairs
      3. Generate embeddings
      4. Insert vectors into Postgres
      5. Upload processed JSON back to S3

    Args:
        job_id:        Unique job identifier (from RQ)
        s3_key:        S3 key of the raw .txt upload
        reciever_data: Dict with sender_name, reciever_name, sender_id, reciever_id
    """
    # Converted the dict-> Reciever object
    reciever = Reciever(**reciever_data)

    with tempfile.TemporaryDirectory() as tmp:

        txt_path = os.path.join(tmp, "chat.txt")
        json_path = os.path.join(tmp, "pairs.json")

        # 1. Download file from S3
        logger.info(f"[{job_id}] Downloading {s3_key} from S3")
        await download_file_from_s3(s3_key, txt_path)

        # 2. Parse WhatsApp chat into pairs
        logger.info(f"[{job_id}] Parsing chat")
        parsed = await parse_whatsapp_chat(txt_path, reciever)

        # 3. Generate embeddings (uses module-level model — no reload)
        logger.info(f"[{job_id}] Generating embeddings for {parsed['total_pairs']} pairs")
        embedded = await embed_pairs(parsed)

        # 4. Insert vectors into Postgres (own session — no FastAPI Depends)
        logger.info(f"[{job_id}] Inserting vectors into database")
        async with AsyncSessionLocal() as db:
            await insert_vectors(embedded, db)

        # 5. Save + upload processed JSON to S3
        logger.info(f"[{job_id}] Uploading processed JSON to S3")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False)

        with open(json_path, "rb") as f:
            await upload_file_to_s3(f, f"processed/{job_id}.json")

    logger.info(f"[{job_id}] Pipeline completed successfully")


def run_pipeline_sync(job_id: str, s3_key: str, reciever_data: dict):
    """
    Sync wrapper for RQ workers.

    RQ executes jobs in forked processes using synchronous Python,
    so we use asyncio.run() to drive the async pipeline.
    """
    asyncio.run(process_chat_pipeline(job_id, s3_key, reciever_data))