from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
import json
import io
from datetime import datetime

from ..database.database_manager import get_context_service
from ..models.lancedb_models import ContextItemResponse, ContextProjectResponse, ContextItemCreate, ContextProjectCreate

router = APIRouter()

@router.get("/export")
async def export_data():
    """Export all context items and projects as JSON"""
    try:
        service = get_context_service()
        # Get all context items (using get_context_items with high limit)
        context_items = service.get_context_items(limit=10000)
        projects = service.get_projects(limit=10000)
        
        # Convert to response models
        items_data = [
            {
                "id": item.id,
                "title": item.title,
                "content": item.content,
                "content_type": item.content_type,
                "project_id": item.project_id,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            }
            for item in context_items
        ]
        
        projects_data = [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None
            }
            for project in projects
        ]
        
        # Create export data structure
        export_data = {
            "export_info": {
                "export_date": datetime.now().isoformat(),
                "version": "1.0",
                "total_items": len(items_data),
                "total_projects": len(projects_data)
            },
            "context_items": items_data,
            "projects": projects_data
        }
        
        # Create JSON string
        json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cortex_export_{timestamp}.json"
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(json_data.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/import")
async def import_data(file: UploadFile = File(...)):
    """Import context items and projects from JSON file"""
    try:
        service = get_context_service()
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read file content
        content = await file.read()
        
        try:
            data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        
        # Validate export structure
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        if "context_items" not in data or "projects" not in data:
            raise HTTPException(status_code=400, detail="Missing required data sections")
        
        imported_items = 0
        imported_projects = 0
        errors = []
        
        # Import projects first (to maintain foreign key relationships)
        if "projects" in data and isinstance(data["projects"], list):
            for project_data in data["projects"]:
                try:
                    # Create project (skip if already exists by checking all projects)
                    existing_projects = service.get_projects(limit=10000)
                    existing_project = next((p for p in existing_projects if p.name == project_data.get("name")), None)
                    if not existing_project:
                        # Convert dict to Pydantic model
                        project_create = ContextProjectCreate(
                            id=project_data.get("id", ""),  # Use existing ID or generate new one
                            name=project_data.get("name"),
                            description=project_data.get("description", ""),
                            settings=project_data.get("settings", {})
                        )
                        service.create_project(project_create)
                        imported_projects += 1
                except Exception as e:
                    errors.append(f"Project '{project_data.get('name', 'Unknown')}': {str(e)}")
        
        # Import context items
        if "context_items" in data and isinstance(data["context_items"], list):
            for item_data in data["context_items"]:
                try:
                    # Convert dict to Pydantic model
                    item_create = ContextItemCreate(
                        title=item_data.get("title"),
                        content=item_data.get("content"),
                        content_type=item_data.get("content_type", "text"),
                        tags=item_data.get("tags", []),
                        extra_metadata=item_data.get("extra_metadata", {}),
                        source=item_data.get("source"),
                        project_id=item_data.get("project_id")
                    )
                    service.create_context_item(item_create)
                    imported_items += 1
                except Exception as e:
                    errors.append(f"Item '{item_data.get('title', 'Unknown')}': {str(e)}")
        
        return {
            "message": "Import completed",
            "imported_items": imported_items,
            "imported_projects": imported_projects,
            "errors": errors,
            "total_errors": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/export/info")
async def get_export_info():
    """Get information about available data for export"""
    try:
        service = get_context_service()
        context_items = service.get_context_items(limit=10000)
        projects = service.get_projects(limit=10000)
        
        return {
            "total_items": len(context_items),
            "total_projects": len(projects),
            "last_export": None,  # Could be tracked in database
            "export_available": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export info: {str(e)}")

@router.delete("/wipe")
async def wipe_database():
    """Wipe all database content - DANGEROUS OPERATION"""
    try:
        service = get_context_service()
        # Get counts before deletion for response
        context_items = service.get_context_items(limit=10000)
        projects = service.get_projects(limit=10000)
        
        deleted_items = len(context_items)
        deleted_projects = len(projects)
        
        # Hard delete all context items (permanently remove from database)
        for item in context_items:
            service.hard_delete_context_item(item.id)
        
        # Hard delete all projects (permanently remove from database)
        for project in projects:
            service.hard_delete_project(project.id)
        
        return {
            "message": "Database wiped successfully",
            "deleted_items": deleted_items,
            "deleted_projects": deleted_projects,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to wipe database: {str(e)}")
