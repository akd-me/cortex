from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import Optional


class BaseResponse(BaseModel):
    """Base response model"""
    model_config = ConfigDict(from_attributes=True)
    
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True


class HealthResponse(BaseModel):
    """Health check response model"""
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    service: str
    version: Optional[str] = None
    endpoints: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    model_config = ConfigDict(from_attributes=True)
    
    error: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status_code: int
