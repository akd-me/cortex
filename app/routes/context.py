from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.connection import get_db
from ..services.context_service import ContextService
from ..models.context import (
    ContextItemCreate, ContextItemUpdate, ContextItemResponse,
    ContextProjectCreate, ContextProjectUpdate, ContextProjectResponse,
    ContextSearchQuery, ContextSearchResult
)

router = APIRouter()

def get_context_service(db: Session = Depends(get_db)) -> ContextService:
    return ContextService(db)

# Context Item endpoints
@router.post("/items", response_model=ContextItemResponse)
async def create_context_item(
    item: ContextItemCreate,
    service: ContextService = Depends(get_context_service)
):
    """Create a new context item"""
    return service.create_context_item(item)

@router.get("/items/{item_id}", response_model=ContextItemResponse)
async def get_context_item(
    item_id: int,
    service: ContextService = Depends(get_context_service)
):
    """Get a specific context item by ID"""
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
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    service: ContextService = Depends(get_context_service)
):
    """Get context items with optional filters"""
    return service.get_context_items(
        project_id=project_id,
        content_type=content_type,
        tags=tags,
        limit=limit,
        offset=offset
    )

@router.put("/items/{item_id}", response_model=ContextItemResponse)
async def update_context_item(
    item_id: int,
    item_update: ContextItemUpdate,
    service: ContextService = Depends(get_context_service)
):
    """Update a context item"""
    updated_item = service.update_context_item(item_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Context item not found")
    return updated_item

@router.delete("/items/{item_id}")
async def delete_context_item(
    item_id: int,
    service: ContextService = Depends(get_context_service)
):
    """Delete a context item"""
    success = service.delete_context_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Context item not found")
    return {"message": "Context item deleted successfully"}

@router.post("/items/search", response_model=ContextSearchResult)
async def search_context_items(
    search_query: ContextSearchQuery,
    service: ContextService = Depends(get_context_service)
):
    """Search context items"""
    items, total = service.search_context_items(search_query)
    return ContextSearchResult(
        items=items,
        total=total,
        limit=search_query.limit,
        offset=search_query.offset
    )

# Project endpoints
@router.post("/projects", response_model=ContextProjectResponse)
async def create_project(
    project: ContextProjectCreate,
    service: ContextService = Depends(get_context_service)
):
    """Create a new context project"""
    return service.create_project(project)

@router.get("/projects/{project_id}", response_model=ContextProjectResponse)
async def get_project(
    project_id: str,
    service: ContextService = Depends(get_context_service)
):
    """Get a specific project by ID"""
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/projects", response_model=List[ContextProjectResponse])
async def get_projects(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    service: ContextService = Depends(get_context_service)
):
    """Get all projects"""
    return service.get_projects(limit=limit, offset=offset)

@router.put("/projects/{project_id}", response_model=ContextProjectResponse)
async def update_project(
    project_id: str,
    project_update: ContextProjectUpdate,
    service: ContextService = Depends(get_context_service)
):
    """Update a project"""
    updated_project = service.update_project(project_id, project_update)
    if not updated_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated_project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    service: ContextService = Depends(get_context_service)
):
    """Delete a project"""
    success = service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# Statistics endpoint
@router.get("/stats")
async def get_context_stats(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    service: ContextService = Depends(get_context_service)
):
    """Get context statistics"""
    return service.get_context_stats(project_id=project_id)
