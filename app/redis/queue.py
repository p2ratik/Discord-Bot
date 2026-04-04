"""
RQ task queue — single source of truth.

Both the API (enqueue) and the worker (dequeue) import from here.
"""

# ── Windows compatibility patch ──────────────────────────────────────────────
# rq's scheduler.py calls multiprocessing.get_context('fork') at MODULE LEVEL.
# Windows only supports 'spawn'; 'fork' raises ValueError before any app code
# runs. We redirect 'fork' → 'spawn' before importing anything from rq.
import multiprocessing as _mp

_orig_get_context = _mp.get_context

def _patched_get_context(method=None):
    if method == "fork":
        method = "spawn"
    return _orig_get_context(method)

_mp.get_context = _patched_get_context
# ─────────────────────────────────────────────────────────────────────────────

from rq import Queue
from app.redis.redis_conn import redis_conn

task_queue = Queue("pipeline", connection=redis_conn)
