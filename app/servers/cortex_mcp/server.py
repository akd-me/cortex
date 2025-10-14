"""
Main Cortex MCP Server - Modular Implementation
"""
from fastmcp import FastMCP
from fastapi import APIRouter

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
from .routes import router, create_mcp_endpoint_handler

# Initialize FastMCP
mcp = FastMCP("Cortex Context Manager")

# Register tools with FastMCP
mcp.tool()(store_context)
mcp.tool()(retrieve_context)
mcp.tool()(search_context)
mcp.tool()(list_contexts)
mcp.tool()(delete_context)
mcp.tool()(create_project)
mcp.tool()(list_projects)

# Register resources with FastMCP
mcp.resource("cortex://contexts")(get_all_contexts)
mcp.resource("cortex://projects")(get_all_projects)

# Create the MCP endpoint handler
mcp_endpoint = create_mcp_endpoint_handler(mcp)

# Add the MCP endpoint to the router
router.add_api_route("/cortex", mcp_endpoint, methods=["POST"])

# Export the FastMCP instance and router
__all__ = ["mcp", "router", "mcp_endpoint"]
