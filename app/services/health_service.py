from datetime import datetime, timezone
from typing import Dict, Any
from ..config import settings
from ..logger import get_logger

logger = get_logger(__name__)


class HealthService:
    """Service for health check operations"""
    
    @staticmethod
    def get_basic_health() -> Dict[str, Any]:
        """Get basic health status"""
        logger.info("Basic health check requested")
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "akd.dev"
        }
    
    @staticmethod
    def get_detailed_health() -> Dict[str, Any]:
        """Get detailed health status"""
        logger.info("Detailed health check requested")
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "akd.dev",
            "version": settings.APP_VERSION,
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "health": "/health",
                "detailed_health": "/health/detailed"
            }
        }
