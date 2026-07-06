import asyncio
import jwt
import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.auth.models import User
from backend.app.auth.schema import AccountStatusSchema, UserCreateSchema

from backend.app.auth.utils import (
    generate_password_hash,
    generate_username,
    generate_otp,
    verify_password,
    create_activation_token,
)

from datetime import timedelta, timezone, datetime
from backend.app.core.services.activation_email import send_activation_email
from backend.app.core.config import settings
from backend.app.core.loguru_logging import get_logger

logger = get_logger()


class UserAuthService:
    pass
