import asyncio
from enum import Enum
from sqlalchemy import text
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Callable, Awaitable, Optional

from app.core.db import async_session
from app.core.celery_app import celery_app
from app.core.loguru_logging import get_logger

logger = get_logger()


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTED = "started"
    DEGRADED = "degraded"
    DOWN = "down"


class HealthCheck:

    def __init__(self):
        self._services: Dict[str, ServiceStatus] = {}
        self._check_functions: Dict[str, Callable[[], Awaitable[bool]]] = {}
        self._last_check: Dict[str, datetime] = {}
        self._timeouts: Dict[str, float] = {}
        self._retry_delays: Dict[str, float] = {}
        self._max_retries: Dict[str, int] = {}
        self._lock = asyncio.Lock()
        self._dependencies: Dict[str, set[str]] = {}

        self._cache_duration: timedelta = timedelta(seconds=25)
        self._cached_status: Optional[Dict[str, Any]] = None
        self._last_check_time: Optional[datetime] = None

    async def validate_dependencies(
        self, service_name: str, depends_on: list[str]
    ) -> None:
        if not depends_on:
            return

        for dependency in depends_on:
            if dependency not in self._services:
                raise ValueError(
                    f"Dependency '{dependency}' not registered for service '{service_name}'"
                )
