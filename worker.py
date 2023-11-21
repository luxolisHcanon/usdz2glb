import redis
from task_queue import get_task_queue, redis_conn
from rq import Worker, Connection

# Dequeues and executes items from the task_queue
with Connection(redis_conn):
    worker = Worker(get_task_queue())
    worker.work()