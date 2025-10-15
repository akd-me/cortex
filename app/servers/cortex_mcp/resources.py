"""
MCP Resources for Cortex Context Manager
"""
import json
from typing import Dict, Any, List, Optional

try:
    from ...database.database_manager import get_context_service
except ImportError:
    from database.database_manager import get_context_service


def get_all_contexts() -> str:
    """
    Get all context items as a resource.
    
    Returns:
        JSON string containing all context items
    """
    try:
        service = get_context_service()
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
        service = get_context_service()
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
