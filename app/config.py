from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )
    
    # App settings
    APP_TITLE: str = "Cortex"
    APP_DESCRIPTION: str = "A personal development application with health check endpoint"
    APP_VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "info"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Database settings (for future use)
    DATABASE_URL: str = ""
    
    # Security settings (for future use)
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Create settings instance
settings = Settings()
