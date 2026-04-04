from app.redis.redis_conn import redis_conn

# task_queue is intentionally NOT re-exported here.
# Importing rq at package init time triggers rq.scheduler which calls
# multiprocessing.get_context('fork') — unavailable on Windows.
# Import task_queue directly from app.redis.queue where you need it.
__all__ = ["redis_conn"]
