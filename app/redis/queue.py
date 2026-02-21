"""
RQ task queue — single source of truth.

Both the API (enqueue) and the worker (dequeue) import from here.
"""

from rq import Queue
from app.redis.redis_conn import redis_conn

task_queue = Queue("pipeline", connection=redis_conn)
