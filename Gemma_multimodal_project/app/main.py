from fastapi import FastAPI
from app.config import settings
from app.routes import router
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_TITLE,
    version="1.0.0",
    debug=settings.DEBUG,
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_TITLE} is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}