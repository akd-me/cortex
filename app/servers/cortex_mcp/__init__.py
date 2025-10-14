"""
Cortex MCP Server Package

A modular MCP (Model Context Protocol) server for Cortex Context Manager.
This package provides tools, resources, and routes for managing context items and projects.

Modules:
- tools: MCP tool functions for context and project management
- resources: MCP resource functions for data access
- routes: FastAPI routes for MCP endpoints
- server: Main server configuration and setup
"""

from .server import mcp, router, mcp_endpoint
from .tools import (
    store_context,
    retrieve_context,
    search_context,
    list_contexts,
    delete_context,
    create_project,
    list_projects
)
from .resources import get_all_contexts, get_all_projects

__version__ = "1.0.0"
__author__ = "Cortex Team"

__all__ = [
    # Main server components
    "mcp",
    "router", 
    "mcp_endpoint",
    
    # Tool functions
    "store_context",
    "retrieve_context", 
    "search_context",
    "list_contexts",
    "delete_context",
    "create_project",
    "list_projects",
    
    # Resource functions
    "get_all_contexts",
    "get_all_projects"
]
