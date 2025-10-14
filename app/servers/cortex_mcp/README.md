# Cortex MCP Server

A modular MCP (Model Context Protocol) server for Cortex Context Manager. This package provides tools, resources, and routes for managing context items and projects.

## Structure

```
cortex_mcp/
├── __init__.py          # Package initialization and exports
├── server.py            # Main server configuration
├── tools.py             # MCP tool functions
├── resources.py         # MCP resource functions  
├── routes.py            # FastAPI routes
└── README.md           # This file
```

## Modules

### `tools.py`
Contains all MCP tool functions for context and project management:
- `store_context()` - Store a new context item
- `retrieve_context()` - Retrieve a specific context item
- `search_context()` - Search through context items
- `list_contexts()` - List context items with filtering
- `delete_context()` - Delete a context item
- `create_project()` - Create a new project
- `list_projects()` - List all projects

### `resources.py`
Contains MCP resource functions for data access:
- `get_all_contexts()` - Get all context items as JSON
- `get_all_projects()` - Get all projects as JSON

### `routes.py`
Contains FastAPI routes and endpoint handlers:
- `mcp_info()` - MCP server info endpoint
- `mcp_health()` - Health check endpoint
- `create_mcp_endpoint_handler()` - Factory for MCP endpoint handler

### `server.py`
Main server configuration that:
- Initializes FastMCP instance
- Registers all tools and resources
- Creates the MCP endpoint handler
- Exports the configured server components

## Usage

### Basic Usage
```python
from cortex_mcp import mcp, router

# Use the FastMCP instance
# Use the FastAPI router
```

### Advanced Usage
```python
from cortex_mcp import (
    mcp, router, mcp_endpoint,
    store_context, retrieve_context,
    get_all_contexts, get_all_projects
)

# Use individual components as needed
```

## Reusability

This modular structure allows for easy reuse in different contexts:

1. **Standalone MCP Server**: Use `server.py` to create a complete MCP server
2. **Tool Functions**: Import and use individual tool functions
3. **Resource Functions**: Use resource functions for data access
4. **Route Components**: Use FastAPI routes in other applications
5. **Custom Configuration**: Mix and match components as needed

## Dependencies

- `fastmcp` - FastMCP framework
- `fastapi` - FastAPI framework
- Cortex database and service modules

## Version

1.0.0
