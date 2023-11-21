from functools import lru_cache

from redis import Redis
from rq import Queue

redis_conn = Redis(host='localhost', port=6379, db=0)
task_queue = Queue(connection=redis_conn, default_timeout=36000)


@lru_cache()
def get_task_queue():
    return task_queue


def get_job_information(job_id):
    try:
        job = task_queue.fetch_job(job_id)
        return job

    except Exception as err:
        print(f"Fetching job information: {err}")
        return None
