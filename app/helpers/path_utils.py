"""
Path utilities for dynamic path resolution in Cortex
"""
import os
import sys
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """
    Get the project root directory dynamically.
    
    This function looks for the project root by checking for key files
    like package.json, requirements.txt, or the app directory.
    
    Returns:
        Path: The project root directory
    """
    current_path = Path(__file__).resolve()
    
    # Walk up the directory tree to find project root
    for parent in current_path.parents:
        # Check for project indicators
        if any((parent / indicator).exists() for indicator in [
            'package.json',
            'requirements.txt', 
            'app',
            'docker-compose.yml',
            'Dockerfile'
        ]):
            return parent
    
    # Fallback to current working directory
    return Path.cwd()


def get_venv_python_path() -> Optional[str]:
    """
    Get the Python executable path from the virtual environment.
    
    Returns:
        Optional[str]: Path to the Python executable, or None if not found
    """
    project_root = get_project_root()
    
    # Check for common virtual environment locations
    venv_paths = [
        project_root / 'venv' / 'bin' / 'python',
        project_root / 'venv' / 'bin' / 'python3',
        project_root / '.venv' / 'bin' / 'python',
        project_root / '.venv' / 'bin' / 'python3',
        project_root / 'env' / 'bin' / 'python',
        project_root / 'env' / 'bin' / 'python3',
    ]
    
    for venv_path in venv_paths:
        if venv_path.exists() and venv_path.is_file():
            return str(venv_path)
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable
    
    # Fallback to system python
    return 'python3'


def get_database_path() -> str:
    """
    Get the database path, using environment variable or default location.
    
    Returns:
        str: Path to the database file
    """
    # Check environment variable first
    db_path = os.getenv('DATABASE_PATH')
    if db_path:
        return db_path
    
    # Use default location in user's home directory
    home_dir = Path.home()
    cortex_dir = home_dir / '.cortex'
    cortex_dir.mkdir(exist_ok=True)
    
    return str(cortex_dir / 'context.db')


def get_script_path(script_name: str) -> str:
    """
    Get the full path to a script in the project root.
    
    Args:
        script_name: Name of the script file
        
    Returns:
        str: Full path to the script
    """
    project_root = get_project_root()
    return str(project_root / script_name)


def get_app_path() -> str:
    """
    Get the path to the app directory.
    
    Returns:
        str: Path to the app directory
    """
    project_root = get_project_root()
    return str(project_root / 'app')


def get_user_home() -> str:
    """
    Get the user's home directory path.
    
    Returns:
        str: Path to user's home directory
    """
    return str(Path.home())


def generate_mcp_config() -> dict:
    """
    Generate MCP configuration with dynamic paths.
    
    Returns:
        dict: MCP configuration dictionary
    """
    project_root = get_project_root()
    python_path = get_venv_python_path()
    database_path = get_database_path()
    
    config = {
        "description": "MCP configuration for Cursor to connect to Cortex Context Manager",
        "mcpServers": {
            "cortex-local": {
                "command": python_path,
                "args": [get_script_path("run_mcp_server.py")],
                "env": {
                    "DATABASE_PATH": database_path
                }
            },
            "cortex-docker": {
                "command": "python3",
                "args": [get_script_path("run_mcp_docker.py")],
                "env": {}
            }
        }
    }
    
    return config


def generate_docker_mcp_config() -> dict:
    """
    Generate Docker MCP configuration with dynamic paths.
    
    Returns:
        dict: Docker MCP configuration dictionary
    """
    config = {
        "description": "MCP configuration for Cursor to connect to Cortex running in Docker",
        "mcpServers": {
            "cortex-docker": {
                "command": "python3",
                "args": [get_script_path("run_mcp_docker.py")],
                "env": {}
            }
        },
        "alternative_configurations": {
            "docker_stdio_approach": {
                "mcpServers": {
                    "cortex-docker": {
                        "command": "python3",
                        "args": [get_script_path("run_mcp_docker.py")],
                        "env": {}
                    }
                }
            },
            "docker_http_approach": {
                "mcpServers": {
                    "cortex-http": {
                        "command": "python3",
                        "args": [get_script_path("run_mcp_http.py")],
                        "env": {}
                    }
                }
            }
        }
    }
    
    return config


if __name__ == "__main__":
    # Test the path utilities
    print(f"Project root: {get_project_root()}")
    print(f"Python path: {get_venv_python_path()}")
    print(f"Database path: {get_database_path()}")
    print(f"App path: {get_app_path()}")
    print(f"User home: {get_user_home()}")
