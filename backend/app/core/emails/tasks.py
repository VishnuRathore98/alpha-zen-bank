import asyncio
from fastapi_mail import MessageSchema, MessageType, MultipartSubtypeEnum
from backend.app.core.celery_app import celery_app
from backend.app.core.loguru_logging import get_logger
from backend.app.core.emails.config import fastmail


logger = get_logger()

@celery_app.task(
    name="send_email_task",
    bind=True,
    max_retries=3,
    soft_time_limit=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
)