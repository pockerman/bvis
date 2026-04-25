from redis import Redis
from rq import Queue

_redis_conn = Redis(host="redis", port=6379)


_summarization_queue = Queue("summarization-tasks", connection=_redis_conn)
_pdf_task_queue = Queue("pdf-generation-tasks", connection=_redis_conn)


def get_redis_connection():
    global _redis_conn
    return _redis_conn

def get_summarization_work_queue() -> Queue:
    global _summarization_queue
    return _summarization_queue


def get_pdf_generation_work_queue() -> Queue:
    global _pdf_task_queue
    return _pdf_task_queue
