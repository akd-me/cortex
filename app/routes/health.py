from fastapi import APIRouter
from ..services.health_service import HealthService

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint"""
    return HealthService.get_basic_health()


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check endpoint"""
    return HealthService.get_detailed_health()
