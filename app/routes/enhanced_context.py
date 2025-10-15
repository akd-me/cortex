from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..database.database_manager import get_context_service, get_database_manager
from ..models.lancedb_models import (
    ContextItemCreate, ContextItemUpdate, ContextItemResponse,
    ContextProjectCreate, ContextProjectUpdate, ContextProjectResponse,
    ContextSearchQuery, ContextSearchResult, SearchType, ContextStats
)
from ..models.base import BaseResponse, ErrorResponse
from ..logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Context Management"])

@router.get("/database/info", response_model=dict)
async def get_database_info():
    """Get database information and capabilities"""
    try:
        db_manager = get_database_manager()
        return db_manager.get_database_info()
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Context Items
@router.post("/items", response_model=ContextItemResponse)
async def create_context_item(item: ContextItemCreate):
    """Create a new context item with automatic embedding generation"""
    try:
        service = get_context_service()
        return service.create_context_item(item)
    except Exception as e:
        logger.error(f"Failed to create context item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/{item_id}", response_model=ContextItemResponse)
async def get_context_item(item_id: int):
    """Get a context item by ID"""
    try:
        service = get_context_service()
        item = service.get_context_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Context item not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get context item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items", response_model=List[ContextItemResponse])
async def get_context_items(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(50, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get context items with optional filters"""
    try:
        service = get_context_service()
        return service.get_context_items(
            project_id=project_id,
            content_type=content_type,
            tags=tags,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Failed to get context items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/items/{item_id}", response_model=ContextItemResponse)
async def update_context_item(item_id: int, item: ContextItemUpdate):
    """Update a context item"""
    try:
        service = get_context_service()
        updated_item = service.update_context_item(item_id, item)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Context item not found")
        return updated_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update context item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/items/{item_id}", response_model=BaseResponse)
async def delete_context_item(item_id: int):
    """Delete a context item"""
    try:
        service = get_context_service()
        success = service.delete_context_item(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Context item not found")
        return BaseResponse(message=f"Context item {item_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete context item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/items/search", response_model=ContextSearchResult)
async def search_context_items(search_query: ContextSearchQuery):
    """Enhanced search with semantic, keyword, and hybrid options"""
    try:
        service = get_context_service()
        return service.search_context_items(search_query)
    except Exception as e:
        logger.error(f"Failed to search context items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/search/semantic", response_model=ContextSearchResult)
async def semantic_search(
    query: str = Query(..., description="Search query"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    content_types: Optional[List[str]] = Query(None, description="Filter by content types"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(50, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Semantic search using embeddings"""
    try:
        search_query = ContextSearchQuery(
            query=query,
            search_type=SearchType.SEMANTIC,
            project_id=project_id,
            content_types=content_types,
            tags=tags,
            limit=limit,
            offset=offset
        )
        service = get_context_service()
        return service.search_context_items(search_query)
    except Exception as e:
        logger.error(f"Failed to perform semantic search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/search/keyword", response_model=ContextSearchResult)
async def keyword_search(
    query: str = Query(..., description="Search query"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    content_types: Optional[List[str]] = Query(None, description="Filter by content types"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(50, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Keyword search using text matching"""
    try:
        search_query = ContextSearchQuery(
            query=query,
            search_type=SearchType.KEYWORD,
            project_id=project_id,
            content_types=content_types,
            tags=tags,
            limit=limit,
            offset=offset
        )
        service = get_context_service()
        return service.search_context_items(search_query)
    except Exception as e:
        logger.error(f"Failed to perform keyword search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/items/search/hybrid", response_model=ContextSearchResult)
async def hybrid_search(
    query: str = Query(..., description="Search query"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    content_types: Optional[List[str]] = Query(None, description="Filter by content types"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(50, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    semantic_weight: float = Query(0.7, ge=0.0, le=1.0, description="Weight for semantic search")
):
    """Hybrid search combining semantic and keyword search"""
    try:
        search_query = ContextSearchQuery(
            query=query,
            search_type=SearchType.HYBRID,
            project_id=project_id,
            content_types=content_types,
            tags=tags,
            limit=limit,
            offset=offset,
            semantic_weight=semantic_weight
        )
        service = get_context_service()
        return service.search_context_items(search_query)
    except Exception as e:
        logger.error(f"Failed to perform hybrid search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Projects
@router.post("/projects", response_model=ContextProjectResponse)
async def create_project(project: ContextProjectCreate):
    """Create a new context project"""
    try:
        service = get_context_service()
        return service.create_project(project)
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=ContextProjectResponse)
async def get_project(project_id: str):
    """Get a project by ID"""
    try:
        service = get_context_service()
        project = service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_model=List[ContextProjectResponse])
async def get_projects(
    limit: int = Query(50, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Get all projects"""
    try:
        service = get_context_service()
        return service.get_projects(limit=limit, offset=offset)
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/projects/{project_id}", response_model=ContextProjectResponse)
async def update_project(project_id: str, project: ContextProjectUpdate):
    """Update a project"""
    try:
        service = get_context_service()
        updated_project = service.update_project(project_id, project)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/projects/{project_id}", response_model=BaseResponse)
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        service = get_context_service()
        success = service.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return BaseResponse(message=f"Project {project_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics
@router.get("/stats", response_model=ContextStats)
async def get_context_stats(project_id: Optional[str] = Query(None, description="Filter by project ID")):
    """Get context statistics"""
    try:
        service = get_context_service()
        return service.get_context_stats(project_id=project_id)
    except Exception as e:
        logger.error(f"Failed to get context stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

