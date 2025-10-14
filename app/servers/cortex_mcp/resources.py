"""
MCP Resources for Cortex Context Manager
"""
import json
from typing import Dict, Any, List, Optional

try:
    from ...database.connection import get_db_context
    from ...services.context_service import ContextService
except ImportError:
    from database.connection import get_db_context
    from services.context_service import ContextService


def get_all_contexts() -> str:
    """
    Get all context items as a resource.
    
    Returns:
        JSON string containing all context items
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            items = service.get_context_items(limit=100)
            
            contexts = []
            for item in items:
                contexts.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content,
                    "content_type": item.content_type,
                    "tags": item.tags,
                    "project_id": item.project_id,
                    "created_at": item.created_at.isoformat()
                })
            
            return json.dumps({"contexts": contexts}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_all_projects() -> str:
    """
    Get all projects as a resource.
    
    Returns:
        JSON string containing all projects
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            projects = service.get_projects(limit=100)
            
            project_list = []
            for project in projects:
                project_list.append({
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat()
                })
            
            return json.dumps({"projects": project_list}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
