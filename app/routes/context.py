from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from ..database.database_manager import get_context_service
from ..models.lancedb_models import (
    ContextItemCreate, ContextItemUpdate, ContextItemResponse,
    ContextProjectCreate, ContextProjectUpdate, ContextProjectResponse,
    ContextSearchQuery, ContextSearchResult
)

router = APIRouter()

# Context Item endpoints
@router.post("/items", response_model=ContextItemResponse)
async def create_context_item(item: ContextItemCreate):
    """Create a new context item"""
    service = get_context_service()
    return service.create_context_item(item)

@router.get("/items/{item_id}", response_model=ContextItemResponse)
async def get_context_item(item_id: int):
    """Get a specific context item by ID"""
    service = get_context_service()
    item = service.get_context_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Context item not found")
    return item

@router.get("/items", response_model=List[ContextItemResponse])
async def get_context_items(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(50, le=100, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    """Get context items with optional filters"""
    service = get_context_service()
    return service.get_context_items(
        project_id=project_id,
        content_type=content_type,
        tags=tags,
        limit=limit,
        offset=offset
    )

@router.put("/items/{item_id}", response_model=ContextItemResponse)
async def update_context_item(item_id: int, item_update: ContextItemUpdate):
    """Update a context item"""
    service = get_context_service()
    updated_item = service.update_context_item(item_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Context item not found")
    return updated_item

@router.delete("/items/{item_id}")
async def delete_context_item(item_id: int):
    """Delete a context item"""
    service = get_context_service()
    success = service.delete_context_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Context item not found")
    return {"message": "Context item deleted successfully"}

@router.post("/items/search", response_model=ContextSearchResult)
async def search_context_items(search_query: ContextSearchQuery):
    """Search context items"""
    service = get_context_service()
    return service.search_context_items(search_query)

# Project endpoints
@router.post("/projects", response_model=ContextProjectResponse)
async def create_project(project: ContextProjectCreate):
    """Create a new context project"""
    service = get_context_service()
    return service.create_project(project)

@router.get("/projects/{project_id}", response_model=ContextProjectResponse)
async def get_project(project_id: str):
    """Get a specific project by ID"""
    service = get_context_service()
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/projects", response_model=List[ContextProjectResponse])
async def get_projects(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all projects"""
    service = get_context_service()
    return service.get_projects(limit=limit, offset=offset)

@router.put("/projects/{project_id}", response_model=ContextProjectResponse)
async def update_project(project_id: str, project_update: ContextProjectUpdate):
    """Update a project"""
    service = get_context_service()
    updated_project = service.update_project(project_id, project_update)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    service = get_context_service()
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# Statistics endpoint
@router.get("/stats")
async def get_context_stats(
    project_id: Optional[str] = Query(None, description="Filter by project ID")
):
    """Get context statistics"""
    service = get_context_service()
    return service.get_context_stats(project_id=project_id)
