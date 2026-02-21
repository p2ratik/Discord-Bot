"""
RQ Worker entry-point.

Usage (from project root):
    python -m app.redis.worker

The worker will listen on the 'pipeline' queue and execute
jobs dispatched by the API.
"""

import os
from dotenv import load_dotenv

# Load env vars before any app imports so DB / AWS / Redis creds are available.
load_dotenv()

from rq import SimpleWorker
from app.redis.redis_conn import redis_conn
from app.redis.queue import task_queue


def run_worker():
    """Start the RQ worker process (SimpleWorker — no fork)."""
    worker = SimpleWorker(
        queues=[task_queue],
        connection=redis_conn,
        name=f"pipeline-worker-{os.getpid()}",
    )
    worker.work(with_scheduler=False)


if __name__ == "__main__":
    run_worker()
