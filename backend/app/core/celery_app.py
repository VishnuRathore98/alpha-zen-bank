from celery import Celery
from backend.app.core.config import settings

# Creating a Celery application named "worker".
celery_app = Celery(
    "worker",
    # Broker(RabbitMQ) = where tasks wait.
    broker=f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}//",
    # Backend(Redis) = Stores: task status, task result, success/failure info
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
)

celery_app.conf.update(
    # JSON serialization: Celery converts data into JSON before sending/storing.
    task_serializer="json",
    result_serializer="json",
    # Track task started: Useful for progress tracking. (PENDING → STARTED → SUCCESS)
    task_track_started=True,
    # Accept only JSON: Security feature. Prevents weird serialized formats.
    accept_content=["application/json"],
    # Retry backend connection: If Redis temporarily fails, Celery retries connecting 10 times.
    result_backend_always_retry=True,
    result_backend_max_retries=10,
    # Task retries:
    #   If task fails:
    #       retry after 5 mins
    #       max 3 retries
    #   Example:
    #       email service down
    #       temporary API failure
    task_default_retry_delay=5 * 60,
    task_max_retries=3,
    # Time Limits:
    #   Hard limit:
    #       Kills task after 5 mins.
    task_time_limit=5 * 60,
    #   Soft limit:
    #       Raises warning/exception before hard kill. Lets task cleanup gracefully.
    task_soft_time_limit=5 * 60,
    # Queue Settings:
    #   Default queue:
    #       Tasks go into this queue unless specified otherwise.
    task_default_queue="alphazen_tasks",
    #   Create queue automatically:
    #       If queue doesn't exist, Celery creates it.
    task_create_missing_queues=True,
    # Reliability Settings:
    #   Acknowledge late:
    #       Normally:
    #           worker says “I got it”
    #           THEN processes task
    #       Problem:
    #           If worker crashes mid-task → task lost.
    #       With acks_late=True:
    #           acknowledge ONLY after success
    #           So crashed tasks return to queue.
    task_acks_late=True,
    #   Task Reject if worker crashes:
    #       If worker dies while processing,
    #       task goes back to queue.
    #       Prevents silent failures.
    task_reject_on_worker_lost=True,
    # Worker Performance:
    #   Without this:
    #       one worker may grab many tasks unfairly.
    #   With 1:
    #       worker takes only one task at a time.
    #       Better for long-running tasks.
    worker_prefetch_multiplier=1,
    #   Restart worker after X tasks:
    #       Prevents memory leaks.
    #       After 1000 tasks:
    #       worker process restarts fresh.
    worker_max_tasks_per_child=1000,
    # Memory limit:
    #   If worker uses too much memory, restart it.
    worker_max_memory_per_child=5000,
    # Logging:
    #   These control logs format. Makes logs cleaner.
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
    # Task monitoring/events:
    #   task_send_sent_event        Emit event when task queued
    #   When a task is sent to queue,
    #   Celery emits a "task-sent" event.
    #   Meaning:
    #       Task created → event generated
    #       - task-sent
    #       - task-started
    #       - task-succeeded
    task_send_sent_event=True,
    #   worker_send_task_events     Emit execution events
    #   Workers send events about task execution.
    #   task-started
    #   task-succeeded
    #   task-failed
    #   task-retried
    worker_send_task_events=True,
    #   result_extended             Store extra task metadata
    #   Stores extra metadata in task result backend.
    #       you may also get:
    #           worker info
    #           task name
    #           arguments
    #           traceback
    #           retries
    #           timestamps
    result_extended=True,
    # Result cleanup:
    #   result_expires              Auto-delete old task results
    #   Task results expire after: 6 mins
    #   After that:
    #       Redis/backend deletes result
    #   Why?
    #       Otherwise Redis fills up forever.
    result_expires=6 * 60,
)

# Auto Discover Tasks:
#   Celery searches for: app/core/emails/tasks.py, and imports tasks automatically.
celery_app.autodiscover_tasks(
    packages=["app.core.emails"],
    related_name="tasks",
    force=True,
)
