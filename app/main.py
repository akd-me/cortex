from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

try:
    # Try relative imports first (when run as module)
    from .config import settings
    from .middleware.cors import cors_middleware
    from .routes import health, root, mcp_config, data_management, enhanced_context
    from .logger import setup_logging
    from .servers.cortex_mcp.server import router as mcp_router
except ImportError:
    # Fall back to absolute imports (when run directly)
    from config import settings
    from middleware.cors import cors_middleware
    from routes import health, root, mcp_config, data_management, enhanced_context
    from logger import setup_logging
    from servers.cortex_mcp.server import router as mcp_router

# Setup logging
setup_logging()

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(CORSMiddleware, **cors_middleware)

# Include routers
app.include_router(root.router, tags=["root"])
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(enhanced_context.router, prefix="/api/context", tags=["context"])
app.include_router(data_management.router, prefix="/api/data", tags=["data-management"])
app.include_router(mcp_config.router, tags=["mcp-config"])
app.include_router(mcp_router, prefix="/mcp", tags=["mcp-server"])

# Mount static files for Vue.js frontend
dist_path = os.path.join(os.path.dirname(__file__), "assets")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    @app.get("/cortex.png")
    async def serve_cortex_favicon():
        """Serve Cortex favicon"""
        favicon_path = os.path.join(dist_path, "cortex.png")
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path, media_type="image/png")
        return {"error": "Favicon not found"}, 404
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve Vue.js frontend for all non-API routes"""
        # Don't serve frontend for API routes or MCP endpoints
        if full_path.startswith(("api", "docs", "redoc", "health", "openapi.json")):
            return {"error": "Not found"}, 404
            
        # Try to serve the file from dist directory
        file_path = os.path.join(dist_path, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # For SPA routing, serve index.html for all other routes
        index_path = os.path.join(dist_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {"error": "Not found"}, 404

if __name__ == "__main__":
    # Run the main FastAPI application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )
