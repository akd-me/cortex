from fastapi import APIRouter
from datetime import datetime, timezone
from ..config import settings

router = APIRouter()


@router.get("/api/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_TITLE}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docs_url": "/docs"
    }
