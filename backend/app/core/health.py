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

    async def add_service(
        self,
        service_name: str,
        check_function: Callable[[], Awaitable],
        timeout: float = 5.0,
        retry_delay: float = 1.0,
        max_retries: int = 3,
        depends_on: list[str] | None = None,
    ) -> None:
        self._services[service_name] = ServiceStatus.STARTED
        self._check_functions[service_name] = check_function
        self._timeouts[service_name] = timeout
        self._retry_delays[service_name] = retry_delay
        self._max_retries[service_name] = max_retries
        self._last_check[service_name] = datetime.now(timezone.utc)

        if depends_on:
            await self.validate_dependencies(service_name, depends_on)
            self._dependencies[service_name] = set(depends_on)
            logger.info(
                f"Service '{service_name}' registered with dependencies: {depends_on}"
            )

    async def check_database(self) -> bool:
        try:
            # TODO: load models
            # TODO: add logger info
            async with async_session() as session:
                await session.execute(text("SELECT 1"))
                await session.commit()

                self._last_check["database"] = datetime.now(timezone.utc)
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def check_redis(self) -> bool:
        try:
            redis_client = celery_app.backend.client
            redis_client.ping()
            self._last_check["redis"] = datetime.now(timezone.utc)
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    async def check_celery(self) -> bool:
        try:
            inspect = celery_app.control.inspect()
            workers = inspect.ping()

            if not workers:
                conn = celery_app.connection()
                try:
                    conn.ensure_connection(max_retries=3)
                    logger.warning("No celery workers found, but Rabbitmq is reachable")

                    self._last_check["celery"] = datetime.now(timezone.utc)
                    return True
                finally:
                    conn.close()

            self._last_check["celery"] = datetime.now(timezone.utc)
            return True

        except Exception as e:
            logger.error(f"Celery health check failed: {e}")
            return False

    async def check_service_health(
        self, service_name: str, max_retries: int = 3
    ) -> ServiceStatus:
        if service_name in self._dependencies:
            for dependency in self._dependencies[service_name]:
                dependency_status = self.check_service_health(dependency)

                if dependency_status != ServiceStatus.HEALTHY:
                    logger.error(
                        f"Dependency {dependency} not healthy for service {service_name}"
                    )
                    return ServiceStatus.DEGRADED

        if service_name not in self._check_functions:
            raise ValueError(f"Unknown service: {service_name}")
        check_function = self._check_functions[service_name]
        timeout = self._timeouts.get(service_name, 5.0)
        max_retries = self._max_retries[service_name]
        retry_delay = self._retry_delays[service_name]

        metrics = {"attempts":0, "total_delay":0.0, "last_error":None}

        for attempt in range(max_retries):
            metrics["attempts"] += 1
            try:
                async with asyncio.timeout(timeout):
                    is_healthy = await check_function()

                    if is_healthy:
                        async with self._lock:
                            self._services[service_name] = ServiceStatus.HEALTHY
                            self._last_check[service_name] = datetime.now()

                            if attempt>0:
                                logger.info(
                                    f"Service {service_name} recovered after {metrics['attempts']} attempts"
                                )
                        return ServiceStatus.HEALTHY

                    async with self._lock:
                        self._services[service_name] = ServiceStatus.DEGRADED
                        