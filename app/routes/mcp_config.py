"""
MCP Configuration API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
import sys
import os
from pathlib import Path

# Add the app directory to the path so we can import our utilities
current_dir = Path(__file__).parent.parent.parent
app_dir = current_dir / 'app'
sys.path.insert(0, str(app_dir))

try:
    from helpers.path_utils import (
        generate_mcp_config, 
        generate_docker_mcp_config,
        get_project_root,
        get_venv_python_path,
        get_database_path,
        get_script_path,
        get_user_home
    )
except ImportError:
    # Fallback if path_utils is not available
    def get_project_root():
        return Path(__file__).parent.parent.parent
    
    def get_venv_python_path():
        return sys.executable
    
    def get_database_path():
        return os.getenv('DATABASE_PATH', str(Path.home() / '.cortex' / 'context.db'))
    
    def get_script_path(script_name):
        return str(get_project_root() / script_name)
    
    def get_user_home():
        return str(Path.home())
    
    def generate_mcp_config():
        return {
            "mcpServers": {
                "cortex-local": {
                    "command": get_venv_python_path(),
                    "args": [get_script_path("run_mcp_server.py")],
                    "env": {
                        "DATABASE_PATH": get_database_path()
                    }
                }
            }
        }
    
    def generate_docker_mcp_config():
        return {
            "mcpServers": {
                "cortex-docker": {
                    "command": "python3",
                    "args": [get_script_path("run_mcp_docker.py")],
                    "env": {}
                }
            }
        }

router = APIRouter(prefix="/api/mcp", tags=["mcp-config"])

@router.get("/config")
async def get_mcp_config() -> Dict[str, Any]:
    """
    Get dynamic MCP configuration based on current environment
    """
    try:
        # Get system information
        system_info = {
            "project_root": str(get_project_root()),
            "python_path": get_venv_python_path(),
            "database_path": get_database_path(),
            "user_home": get_user_home(),
        }
        
        return {
            "success": True,
            "system_info": system_info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate MCP configuration: {str(e)}")

@router.get("/config/cursor")
async def get_cursor_config() -> Dict[str, Any]:
    """
    Get Cursor IDE specific MCP configuration
    """
    try:
        local_config = generate_mcp_config()
        docker_config = generate_docker_mcp_config()
        
        # Combine both configurations for Cursor
        cursor_config = {
            "mcpServers": {
                **local_config["mcpServers"],
                **docker_config["mcpServers"]
            }
        }
        
        return {
            "success": True,
            "config": cursor_config,
            "config_json": json.dumps(cursor_config, indent=2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Cursor configuration: {str(e)}")