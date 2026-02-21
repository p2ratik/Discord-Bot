"""
Shared Redis connection used by the RQ queue and worker.

Reads credentials from environment variables with safe defaults
so it works both inside the FastAPI process and in standalone workers.
"""

import os
from dotenv import load_dotenv
import redis

load_dotenv()

redis_conn = redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=False  # required for RQ
)