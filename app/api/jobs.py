from fastapi import APIRouter, HTTPException
from rq.job import Job
from app.redis.redis_conn import redis_conn
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["jobs"])


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Poll the status of a queued pipeline job.

    Returns:
        status:  queued | started | finished | failed | deferred | canceled
        result:  job return value (if finished)
        error:   traceback string (if failed)
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        logger.warning(f"Job not found: {job_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    response = {
        "job_id": job.id,
        "status": job.get_status(),
    }

    if job.is_finished:
        response["result"] = job.result
    elif job.is_failed:
        response["error"] = job.exc_info

    return response
