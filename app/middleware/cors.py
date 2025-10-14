from ..config import settings

# CORS middleware configuration
cors_middleware = {
    "allow_origins": settings.CORS_ORIGINS,
    "allow_credentials": settings.CORS_CREDENTIALS,
    "allow_methods": settings.CORS_METHODS,
    "allow_headers": settings.CORS_HEADERS,
}
