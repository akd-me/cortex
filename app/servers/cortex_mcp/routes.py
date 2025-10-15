"""
FastAPI Routes for Cortex MCP Server
"""
from fastapi import APIRouter, Request
from typing import Dict, Any
import json

# Create FastAPI router for MCP endpoints
router = APIRouter()


@router.get("/cortex/info")
async def mcp_info():
    """MCP server info endpoint for dashboard"""
    return {
        "name": "Cortex Context Manager",
        "version": "1.0.0",
        "description": "Local context storage and retrieval system",
        "mcp_server": {
            "host": "localhost",
            "port": 8001
        },
        "capabilities": {
            "tools": [
                {"name": "store_context", "description": "Store a new context item"},
                {"name": "retrieve_context", "description": "Retrieve a specific context item"},
                {"name": "search_context", "description": "Search through stored context items"},
                {"name": "list_contexts", "description": "List context items with optional filtering"},
                {"name": "delete_context", "description": "Delete a context item"},
                {"name": "create_project", "description": "Create a new project"},
                {"name": "list_projects", "description": "List all projects"}
            ]
        },
        "protocol": "mcp",
        "endpoints": {
            "mcp": "/mcp/cortex",
            "health": "/mcp/cortex/health"
        }
    }

@router.get("/cortex")
async def mcp_cortex_info():
    """MCP server info endpoint"""
    return {
        "name": "Cortex Context Manager",
        "version": "1.0.0",
        "description": "Local context storage and retrieval system",
        "protocol": "mcp",
        "endpoints": {
            "mcp": "/mcp/cortex",
            "health": "/mcp/cortex/health"
        }
    }


@router.get("/cortex/health")
async def mcp_health():
    """Health check endpoint for the MCP server"""
    return {
        "status": "healthy",
        "service": "cortex-mcp-server",
        "version": "1.0.0",
        "endpoint": "/mcp/cortex"
    }


def create_mcp_endpoint_handler(mcp_instance):
    """
    Create the MCP endpoint handler that uses the provided MCP instance.
    
    Args:
        mcp_instance: The FastMCP instance to use for tool execution
    
    Returns:
        The endpoint handler function
    """
    async def mcp_endpoint(request: Request):
        """Handle MCP requests with proper FastMCP integration"""
        try:
            # Parse the JSON body from the request
            body = await request.json()
            method = body.get("method", "")
            request_id = body.get("id", 1)
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "experimental": {},
                            "prompts": {"listChanged": True},
                            "resources": {"subscribe": False, "listChanged": True},
                            "tools": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "Cortex Context Manager",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "initialized":
                # Handle initialized notification (no response needed)
                return None
            elif method == "tools/list":
                # Return predefined tool schemas
                tools = [
                    {
                        "name": "store_context",
                        "description": "Store a new context item in the local database",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"},
                                "content_type": {"type": "string", "default": "text"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "project_id": {"type": "string"},
                                "extra_metadata": {"type": "object"}
                            },
                            "required": ["title", "content"]
                        }
                    },
                    {
                        "name": "retrieve_context",
                        "description": "Retrieve a specific context item by its ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "context_id": {"type": "integer"}
                            },
                            "required": ["context_id"]
                        }
                    },
                    {
                        "name": "search_context",
                        "description": "Search through stored context items",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "content_types": {"type": "array", "items": {"type": "string"}},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "project_id": {"type": "string"},
                                "limit": {"type": "integer", "default": 10}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "list_contexts",
                        "description": "List context items with optional filtering",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "content_type": {"type": "string"},
                                "limit": {"type": "integer", "default": 20},
                                "offset": {"type": "integer", "default": 0}
                            }
                        }
                    },
                    {
                        "name": "delete_context",
                        "description": "Delete a context item",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "context_id": {"type": "integer"}
                            },
                            "required": ["context_id"]
                        }
                    },
                    {
                        "name": "create_project",
                        "description": "Create a new project for organizing context items",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "settings": {"type": "object"}
                            },
                            "required": ["project_id", "name"]
                        }
                    },
                    {
                        "name": "list_projects",
                        "description": "List all projects",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "limit": {"type": "integer", "default": 20},
                                "offset": {"type": "integer", "default": 0}
                            }
                        }
                    }
                ]
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                }
            elif method == "tools/call":
                # Handle tool execution using FastMCP
                params = body.get("params", {})
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                
                try:
                    # Get the tool from FastMCP
                    tool = mcp_instance._tool_manager._tools.get(tool_name)
                    if not tool:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Tool not found: {tool_name}"
                            }
                        }
                    
                    # Execute the tool
                    result = await tool.run(arguments)
                    
                    # Format the result properly
                    if hasattr(result, 'content'):
                        content = result.content
                    else:
                        content = str(result)
                    
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": str(content)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution error: {str(e)}"
                        }
                    }
            elif method == "resources/list":
                # Get resources from FastMCP server
                resources = []
                for resource_name, resource in mcp_instance._resource_manager._resources.items():
                    resources.append({
                        "uri": resource_name,
                        "name": getattr(resource, 'name', resource_name),
                        "description": getattr(resource, 'description', ''),
                        "mimeType": "application/json"
                    })
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"resources": resources}
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": body.get("id", 1),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    return mcp_endpoint
