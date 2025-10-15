import os
import lancedb
import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import pyarrow as pa
from ..logger import get_logger
from ..services.embeddings_service import EmbeddingsService

logger = get_logger(__name__)

class LanceDBConnection:
    """LanceDB connection and operations manager"""
    
    def __init__(self, db_path: Optional[str] = None, model_name: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path or os.path.join(os.path.expanduser("~/.cortex"), "lancedb")
        self.model_name = model_name
        self.db = None
        self.embeddings_service = None
        self.context_table = None
        self.projects_table = None
        self._initialize()
    
    def _initialize(self):
        """Initialize LanceDB connection and tables"""
        try:
            # Ensure database directory exists
            os.makedirs(self.db_path, exist_ok=True)
            
            # Initialize LanceDB
            self.db = lancedb.connect(self.db_path)
            logger.info(f"Connected to LanceDB at: {self.db_path}")
            
            # Initialize embeddings service
            self.embeddings_service = EmbeddingsService(self.model_name)
            
            # Initialize tables
            self._initialize_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}")
            raise
    
    def _initialize_tables(self):
        """Initialize LanceDB tables"""
        try:
            # Check if context table exists
            if "context_items" not in self.db.table_names():
                self._create_context_table()
            else:
                self.context_table = self.db.open_table("context_items")
                logger.info("Opened existing context_items table")
            
            # Check if projects table exists
            if "context_projects" not in self.db.table_names():
                self._create_projects_table()
            else:
                self.projects_table = self.db.open_table("context_projects")
                logger.info("Opened existing context_projects table")
                
        except Exception as e:
            logger.error(f"Failed to initialize tables: {e}")
            raise
    
    def _create_context_table(self):
        """Create the context items table with embeddings"""
        try:
            # Create empty table with schema
            schema = pa.schema([
                pa.field("id", pa.int64()),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("content_type", pa.string()),
                pa.field("tags", pa.list_(pa.string())),
                pa.field("extra_metadata", pa.string()),  # JSON as string
                pa.field("is_active", pa.bool_()),
                pa.field("created_at", pa.timestamp('us')),
                pa.field("updated_at", pa.timestamp('us')),
                pa.field("source", pa.string()),
                pa.field("project_id", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), list_size=384))  # Fixed-size vector for embeddings
            ])
            
            # Create empty table
            empty_data = []
            self.context_table = self.db.create_table("context_items", empty_data, schema=schema)
            logger.info("Created context_items table with embeddings support")
            
        except Exception as e:
            logger.error(f"Failed to create context table: {e}")
            raise
    
    def _create_projects_table(self):
        """Create the projects table"""
        try:
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("name", pa.string()),
                pa.field("description", pa.string()),
                pa.field("settings", pa.string()),  # JSON as string
                pa.field("is_active", pa.bool_()),
                pa.field("created_at", pa.timestamp('us')),
                pa.field("updated_at", pa.timestamp('us'))
            ])
            
            empty_data = []
            self.projects_table = self.db.create_table("context_projects", empty_data, schema=schema)
            logger.info("Created context_projects table")
            
        except Exception as e:
            logger.error(f"Failed to create projects table: {e}")
            raise
    
    def add_context_item(self, item_data: Dict[str, Any]) -> int:
        """Add a context item with embeddings"""
        try:
            # Generate embeddings for title and content
            text_for_embedding = f"{item_data['title']} {item_data['content']}"
            embedding = self.embeddings_service.encode_documents([text_for_embedding])[0]
            
            # Prepare data for insertion
            data = {
                "id": item_data.get("id"),
                "title": item_data["title"],
                "content": item_data["content"],
                "content_type": item_data.get("content_type", "text"),
                "tags": item_data.get("tags", []),
                "extra_metadata": str(item_data.get("extra_metadata", {})),
                "is_active": item_data.get("is_active", True),
                "created_at": item_data.get("created_at", datetime.now()),
                "updated_at": item_data.get("updated_at"),
                "source": item_data.get("source"),
                "project_id": item_data.get("project_id"),
                "vector": embedding.tolist()
            }
            
            # Insert into table
            self.context_table.add([data])
            logger.info(f"Added context item: {item_data['title']}")
            return data["id"]
            
        except Exception as e:
            logger.error(f"Failed to add context item: {e}")
            raise
    
    def add_project(self, project_data: Dict[str, Any]) -> str:
        """Add a project"""
        try:
            data = {
                "id": project_data["id"],
                "name": project_data["name"],
                "description": project_data.get("description"),
                "settings": str(project_data.get("settings", {})),
                "is_active": project_data.get("is_active", True),
                "created_at": project_data.get("created_at", datetime.now()),
                "updated_at": project_data.get("updated_at")
            }
            
            self.projects_table.add([data])
            logger.info(f"Added project: {project_data['name']}")
            return data["id"]
            
        except Exception as e:
            logger.error(f"Failed to add project: {e}")
            raise
    
    def semantic_search(self, query: str, limit: int = 50, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform semantic search on context items"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings_service.encode_query(query)
            
            # Build search query with explicit vector column name
            search_query = self.context_table.search(query_embedding, vector_column_name="vector").limit(limit * 2)  # Get more results for filtering
            
            # Execute search first
            results = search_query.to_pandas()
            
            # Apply filters in Python since LanceDB where clauses can be tricky
            if filters:
                if filters.get("is_active") is not None:
                    results = results[results['is_active'] == filters['is_active']]
                if filters.get("project_id"):
                    results = results[results['project_id'] == filters['project_id']]
                if filters.get("content_type"):
                    results = results[results['content_type'] == filters['content_type']]
            
            # Apply final limit
            if limit > 0:
                results = results.head(limit)
            
            # Convert to list of dicts
            return results.to_dict('records')
            
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            raise
    
    def keyword_search(self, query: str, limit: int = 50, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform keyword search on context items"""
        try:
            # Get all data and filter in Python since LanceDB doesn't support ILIKE
            all_data = self.context_table.to_pandas()
            
            # Apply text search filters
            if query.strip():
                query_lower = query.lower()
                text_match = all_data['title'].str.lower().str.contains(query_lower, na=False) | \
                           all_data['content'].str.lower().str.contains(query_lower, na=False)
                all_data = all_data[text_match]
            
            # Apply additional filters
            if filters:
                if filters.get("is_active") is not None:
                    all_data = all_data[all_data['is_active'] == filters['is_active']]
                if filters.get("project_id"):
                    all_data = all_data[all_data['project_id'] == filters['project_id']]
                if filters.get("content_type"):
                    all_data = all_data[all_data['content_type'] == filters['content_type']]
            
            # Apply limit
            if limit > 0:
                all_data = all_data.head(limit)
            
            return all_data.to_dict('records')
            
        except Exception as e:
            logger.error(f"Failed to perform keyword search: {e}")
            raise
    
    def hybrid_search(self, query: str, limit: int = 50, semantic_weight: float = 0.7, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword search"""
        try:
            # Get semantic search results
            semantic_results = self.semantic_search(query, limit * 2, filters)
            
            # Get keyword search results
            keyword_results = self.keyword_search(query, limit * 2, filters)
            
            # Combine and score results
            combined_results = self._combine_search_results(
                semantic_results, keyword_results, semantic_weight
            )
            
            return combined_results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to perform hybrid search: {e}")
            raise
    
    def _combine_search_results(self, semantic_results: List[Dict], keyword_results: List[Dict], semantic_weight: float) -> List[Dict]:
        """Combine and score search results"""
        # Create a dictionary to store combined scores
        combined_scores = {}
        
        # Process semantic results
        for i, result in enumerate(semantic_results):
            item_id = result.get("id")
            semantic_score = 1.0 - (i / len(semantic_results))  # Normalize by rank
            combined_scores[item_id] = {
                "item": result,
                "semantic_score": semantic_score,
                "keyword_score": 0.0
            }
        
        # Process keyword results
        for i, result in enumerate(keyword_results):
            item_id = result.get("id")
            keyword_score = 1.0 - (i / len(keyword_results))  # Normalize by rank
            
            if item_id in combined_scores:
                combined_scores[item_id]["keyword_score"] = keyword_score
            else:
                combined_scores[item_id] = {
                    "item": result,
                    "semantic_score": 0.0,
                    "keyword_score": keyword_score
                }
        
        # Calculate final scores and sort
        final_results = []
        for item_id, scores in combined_scores.items():
            final_score = (semantic_weight * scores["semantic_score"] + 
                          (1 - semantic_weight) * scores["keyword_score"])
            scores["item"]["combined_score"] = final_score
            final_results.append(scores["item"])
        
        # Sort by combined score
        final_results.sort(key=lambda x: x["combined_score"], reverse=True)
        return final_results
    
    def get_context_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get a context item by ID"""
        try:
            results = self.context_table.search().where(f"id = {item_id}").to_pandas()
            if not results.empty:
                return results.iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get context item {item_id}: {e}")
            return None
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID"""
        try:
            results = self.projects_table.search().where(f"id = '{project_id}'").to_pandas()
            if not results.empty:
                return results.iloc[0].to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            return None
    
    def update_context_item(self, item_id: int, update_data: Dict[str, Any]) -> bool:
        """Update a context item"""
        try:
            # Get existing item
            existing_item = self.get_context_item(item_id)
            if not existing_item:
                return False
            
            # Update fields
            for key, value in update_data.items():
                if key in existing_item:
                    existing_item[key] = value
            
            # Regenerate embeddings if content changed
            if "title" in update_data or "content" in update_data:
                text_for_embedding = f"{existing_item['title']} {existing_item['content']}"
                embedding = self.embeddings_service.encode_documents([text_for_embedding])[0]
                existing_item["vector"] = embedding.tolist()
            
            # Update timestamp
            existing_item["updated_at"] = datetime.now()
            
            # Delete old record and add updated one
            self.context_table.delete(f"id = {item_id}")
            self.context_table.add([existing_item])
            
            logger.info(f"Updated context item {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update context item {item_id}: {e}")
            return False
    
    def delete_context_item(self, item_id: int) -> bool:
        """Soft delete a context item"""
        try:
            return self.update_context_item(item_id, {"is_active": False})
        except Exception as e:
            logger.error(f"Failed to delete context item {item_id}: {e}")
            return False
    
    def hard_delete_context_item(self, item_id: int) -> bool:
        """Hard delete a context item (permanently remove from database)"""
        try:
            self.context_table.delete(f"id = {item_id}")
            logger.info(f"Hard deleted context item {item_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to hard delete context item {item_id}: {e}")
            return False
    
    def hard_delete_project(self, project_id: str) -> bool:
        """Hard delete a project (permanently remove from database)"""
        try:
            self.projects_table.delete(f"id = '{project_id}'")
            logger.info(f"Hard deleted project {project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to hard delete project {project_id}: {e}")
            return False
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get statistics about the tables"""
        try:
            # Count only active items
            context_data = self.context_table.to_pandas()
            active_context_count = len(context_data[context_data['is_active'] == True]) if not context_data.empty else 0
            
            projects_data = self.projects_table.to_pandas()
            active_projects_count = len(projects_data[projects_data['is_active'] == True]) if not projects_data.empty else 0
            
            return {
                "context_items_count": active_context_count,
                "projects_count": active_projects_count,
                "embedding_dimension": self.embeddings_service.get_embedding_dimension()
            }
        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return {}
