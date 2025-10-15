import os
from typing import Optional, Union
from contextlib import contextmanager
from ..database.lancedb_connection import LanceDBConnection
from ..services.lancedb_context_service import LanceDBContextService
from ..logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Database manager that uses LanceDB exclusively"""
    
    def __init__(self, lancedb_path: Optional[str] = None):
        self.lancedb_connection = None
        self.lancedb_service = None
        
        self._initialize_lancedb(lancedb_path)
    
    def _initialize_lancedb(self, lancedb_path: Optional[str] = None):
        """Initialize LanceDB connection and services"""
        try:
            # Use environment variable or default path
            if not lancedb_path:
                lancedb_path = os.getenv("LANCEDB_PATH", os.path.join(os.path.expanduser("~/.cortex"), "lancedb"))
            
            # Initialize LanceDB connection
            self.lancedb_connection = LanceDBConnection(lancedb_path)
            
            # Initialize LanceDB service
            self.lancedb_service = LanceDBContextService(self.lancedb_connection)
            
            logger.info("LanceDB database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}")
            raise
    
    def get_context_service(self):
        """Get the LanceDB context service"""
        if not self.lancedb_service:
            raise RuntimeError("LanceDB service not initialized")
        return self.lancedb_service
    
    
    def get_lancedb_connection(self):
        """Get the LanceDB connection"""
        return self.lancedb_connection
    
    def is_lancedb_available(self) -> bool:
        """Check if LanceDB is available and initialized"""
        return self.lancedb_connection is not None
    
    def get_database_info(self) -> dict:
        """Get information about the current database setup"""
        info = {
            "using_lancedb": True,
            "lancedb_available": self.is_lancedb_available()
        }
        
        if self.is_lancedb_available():
            try:
                stats = self.lancedb_connection.get_table_stats()
                info.update({
                    "lancedb_stats": stats,
                    "embedding_model": "all-MiniLM-L6-v2",
                    "search_capabilities": ["semantic", "keyword", "hybrid"]
                })
            except Exception as e:
                info["lancedb_error"] = str(e)
        
        return info

# Global database manager instance
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        lancedb_path = os.getenv("LANCEDB_PATH")
        _db_manager = DatabaseManager(lancedb_path=lancedb_path)
    return _db_manager

def get_context_service():
    """Get the LanceDB context service"""
    return get_database_manager().get_context_service()


@contextmanager
def get_db_context():
    """Context manager for database sessions (backward compatibility)"""
    # For LanceDB, we don't need a session context
    yield None
