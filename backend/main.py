from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import router
from app.core.loguru_logging import logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(router, prefix=settings.API_V1_STR)


@app.get("/")
def home():
    logger.info("Info log from home")
    logger.debug("Debug log from home")
    logger.warning("Warning log from home")
    logger.error("Error log from home")
    logger.critical("Critical log from home")
    return {"message": "Welcome to the AlphaZen smart bank."}
