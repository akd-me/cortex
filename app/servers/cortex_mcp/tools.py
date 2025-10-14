"""
MCP Tools for Cortex Context Manager
"""
from typing import Dict, Any, List, Optional

try:
    from ...database.connection import get_db_context
    from ...services.context_service import ContextService
    from ...models.context import (
        ContextItemCreate, 
        ContextProjectCreate,
        ContextSearchQuery
    )
except ImportError:
    from database.connection import get_db_context
    from services.context_service import ContextService
    from models.context import (
        ContextItemCreate, 
        ContextProjectCreate,
        ContextSearchQuery
    )


def store_context(
    title: str,
    content: str,
    content_type: str = "text",
    tags: List[str] = None,
    project_id: Optional[str] = None,
    extra_metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Store a new context item in the local database.
    
    Args:
        title: Title of the context item
        content: The main content/text of the context
        content_type: Type of content (text, code, markdown, json)
        tags: List of tags for categorization
        project_id: Optional project ID to associate with
        extra_metadata: Additional metadata as key-value pairs
    
    Returns:
        Dictionary with success status and created item details
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            
            context_data = ContextItemCreate(
                title=title,
                content=content,
                content_type=content_type,
                tags=tags or [],
                project_id=project_id,
                extra_metadata=extra_metadata or {},
                source="mcp_client"
            )
            
            result = service.create_context_item(context_data)
            
            return {
                "success": True,
                "message": "Context stored successfully",
                "data": {
                    "id": result.id,
                    "title": result.title,
                    "created_at": result.created_at.isoformat()
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to store context"
        }


def retrieve_context(context_id: int) -> Dict[str, Any]:
    """
    Retrieve a specific context item by its ID.
    
    Args:
        context_id: The unique ID of the context item
    
    Returns:
        Dictionary with the context item details or error
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            context_item = service.get_context_item(context_id)
            
            if not context_item:
                return {
                    "success": False,
                    "error": "Context not found",
                    "message": f"No context found with ID {context_id}"
                }
            
            return {
                "success": True,
                "data": {
                    "id": context_item.id,
                    "title": context_item.title,
                    "content": context_item.content,
                    "content_type": context_item.content_type,
                    "tags": context_item.tags,
                    "extra_metadata": context_item.extra_metadata,
                    "project_id": context_item.project_id,
                    "created_at": context_item.created_at.isoformat(),
                    "updated_at": context_item.updated_at.isoformat() if context_item.updated_at else None
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve context"
        }


def search_context(
    query: str,
    content_types: List[str] = None,
    tags: List[str] = None,
    project_id: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Search through stored context items.
    
    Args:
        query: Search query to match against title and content
        content_types: Filter by specific content types
        tags: Filter by specific tags
        project_id: Filter by project ID
        limit: Maximum number of results to return (default: 10, max: 50)
    
    Returns:
        Dictionary with search results
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            
            search_query = ContextSearchQuery(
                query=query,
                content_types=content_types,
                tags=tags,
                project_id=project_id,
                limit=min(limit, 50),
                offset=0
            )
            
            items, total = service.search_context_items(search_query)
            
            results = []
            for item in items:
                results.append({
                    "id": item.id,
                    "title": item.title,
                    "content": item.content[:500] + "..." if len(item.content) > 500 else item.content,
                    "content_type": item.content_type,
                    "tags": item.tags,
                    "project_id": item.project_id,
                    "created_at": item.created_at.isoformat()
                })
            
            return {
                "success": True,
                "data": {
                    "results": results,
                    "total": total,
                    "query": query,
                    "limit": limit
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search context"
        }


def list_contexts(
    project_id: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List context items with optional filtering.
    
    Args:
        project_id: Filter by project ID
        content_type: Filter by content type
        limit: Maximum number of items to return
        offset: Number of items to skip (for pagination)
    
    Returns:
        Dictionary with list of context items
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            
            items = service.get_context_items(
                project_id=project_id,
                content_type=content_type,
                limit=min(limit, 50),
                offset=offset
            )
            
            results = []
            for item in items:
                results.append({
                    "id": item.id,
                    "title": item.title,
                    "content_type": item.content_type,
                    "tags": item.tags,
                    "project_id": item.project_id,
                    "created_at": item.created_at.isoformat()
                })
            
            return {
                "success": True,
                "data": {
                    "items": results,
                    "count": len(results),
                    "offset": offset,
                    "limit": limit
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list contexts"
        }


def delete_context(context_id: int) -> Dict[str, Any]:
    """
    Delete a context item.
    
    Args:
        context_id: The unique ID of the context item to delete
    
    Returns:
        Dictionary with success status
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            success = service.delete_context_item(context_id)
            
            if not success:
                return {
                    "success": False,
                    "error": "Context not found",
                    "message": f"No context found with ID {context_id}"
                }
            
            return {
                "success": True,
                "message": f"Context {context_id} deleted successfully"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to delete context"
        }


def create_project(
    project_id: str,
    name: str,
    description: Optional[str] = None,
    settings: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a new project for organizing context items.
    
    Args:
        project_id: Unique identifier for the project
        name: Human-readable name for the project
        description: Optional description of the project
        settings: Optional project settings as key-value pairs
    
    Returns:
        Dictionary with success status and project details
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            
            project_data = ContextProjectCreate(
                id=project_id,
                name=name,
                description=description,
                settings=settings or {}
            )
            
            result = service.create_project(project_data)
            
            return {
                "success": True,
                "message": "Project created successfully",
                "data": {
                    "id": result.id,
                    "name": result.name,
                    "created_at": result.created_at.isoformat()
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create project"
        }


def list_projects(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    List all projects.
    
    Args:
        limit: Maximum number of projects to return
        offset: Number of projects to skip (for pagination)
    
    Returns:
        Dictionary with list of projects
    """
    try:
        with get_db_context() as db:
            service = ContextService(db)
            projects = service.get_projects(limit=min(limit, 50), offset=offset)
            
            results = []
            for project in projects:
                results.append({
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat()
                })
            
            return {
                "success": True,
                "data": {
                    "projects": results,
                    "count": len(results),
                    "offset": offset,
                    "limit": limit
                }
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list projects"
        }
