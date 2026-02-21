import boto3
import os
import asyncio
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )
    logger.info("Boto3 client created successfully")
except Exception as e:
    logger.error(f'Failed to create Boto3 client: {e}')
    raise

BUCKET = os.getenv("S3_BUCKET_NAME")

async def upload_file_to_s3(file, s3_key: str):
    """Uploads the file to the s3 bucket"""
    await asyncio.to_thread(s3.upload_fileobj, file, BUCKET, s3_key)
    return s3_key

async def download_file_from_s3(key, file_path):
    """Downloads file to the temp folder from s3"""
    await asyncio.to_thread(s3.download_file, BUCKET, key, file_path)