import time
import json
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from ..database.lancedb_connection import LanceDBConnection
from ..models.lancedb_models import (
    ContextItemCreate, ContextItemUpdate, ContextItemResponse,
    ContextProjectCreate, ContextProjectUpdate, ContextProjectResponse,
    ContextSearchQuery, ContextSearchResult, SearchType, ContextStats
)
from ..logger import get_logger

logger = get_logger(__name__)

class LanceDBContextService:
    """LanceDB-based context management service"""
    
    def __init__(self, lancedb_connection: LanceDBConnection):
        self.db = lancedb_connection
    
    def _safe_json_parse(self, value):
        """Safely parse JSON string or return dict if already parsed"""
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return {}
        else:
            return {}
    
    def _safe_datetime_parse(self, value):
        """Safely parse datetime value, handling NaT and None"""
        if pd.isna(value) or value is None:
            return None
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return None
        else:
            return None
    
    # Context Item operations
    def create_context_item(self, item_data: ContextItemCreate) -> ContextItemResponse:
        """Create a new context item with embeddings"""
        try:
            # Generate ID (simple auto-increment for now)
            existing_items = self.db.context_table.to_pandas()
            new_id = existing_items['id'].max() + 1 if not existing_items.empty else 1
            
            # Prepare data for insertion
            item_dict = item_data.model_dump()
            item_dict['id'] = new_id
            item_dict['is_active'] = True
            item_dict['created_at'] = datetime.now()
            item_dict['updated_at'] = None
            
            # Add to database
            self.db.add_context_item(item_dict)
            
            # Return response
            return ContextItemResponse(
                id=new_id,
                title=item_data.title,
                content=item_data.content,
                content_type=item_data.content_type,
                tags=item_data.tags,
                extra_metadata=item_data.extra_metadata,
                source=item_data.source,
                project_id=item_data.project_id,
                is_active=True,
                created_at=item_dict['created_at'],
                updated_at=None
            )
            
        except Exception as e:
            logger.error(f"Failed to create context item: {e}")
            raise
    
    def get_context_item(self, item_id: int) -> Optional[ContextItemResponse]:
        """Get a context item by ID"""
        try:
            item_data = self.db.get_context_item(item_id)
            if not item_data or not item_data.get('is_active', True):
                return None
            
            return ContextItemResponse(
                id=item_data['id'],
                title=item_data['title'],
                content=item_data['content'],
                content_type=item_data['content_type'],
                tags=item_data['tags'],
                extra_metadata=self._safe_json_parse(item_data.get('extra_metadata', {})),
                source=item_data['source'],
                project_id=item_data['project_id'],
                is_active=item_data['is_active'],
                created_at=self._safe_datetime_parse(item_data['created_at']),
                updated_at=self._safe_datetime_parse(item_data.get('updated_at'))
            )
            
        except Exception as e:
            logger.error(f"Failed to get context item {item_id}: {e}")
            return None
    
    def get_context_items(
        self, 
        project_id: Optional[str] = None,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ContextItemResponse]:
        """Get context items with optional filters"""
        try:
            # Get all data from table
            results = self.db.context_table.to_pandas()
            
            # Apply filters
            if not results.empty:
                # Filter by is_active
                results = results[results['is_active'] == True]
                
                if project_id:
                    results = results[results['project_id'] == project_id]
                if content_type:
                    results = results[results['content_type'] == content_type]
                if tags:
                    # Filter by tags (any of the provided tags)
                    results = results[results['tags'].apply(lambda x: any(tag in x for tag in tags))]
            
            # Apply offset and limit
            if offset > 0:
                results = results.iloc[offset:]
            if limit > 0:
                results = results.head(limit)
            
            # Convert to response objects
            items = []
            for _, row in results.iterrows():
                items.append(ContextItemResponse(
                    id=int(row['id']),
                    title=row['title'],
                    content=row['content'],
                    content_type=row['content_type'],
                    tags=row['tags'],
                    extra_metadata=self._safe_json_parse(row.get('extra_metadata', {})),
                    source=row['source'],
                    project_id=row['project_id'],
                    is_active=bool(row['is_active']),
                    created_at=self._safe_datetime_parse(row['created_at']),
                    updated_at=self._safe_datetime_parse(row.get('updated_at'))
                ))
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to get context items: {e}")
            return []
    
    def update_context_item(self, item_id: int, item_data: ContextItemUpdate) -> Optional[ContextItemResponse]:
        """Update a context item"""
        try:
            # Get existing item
            existing_item = self.get_context_item(item_id)
            if not existing_item:
                return None
            
            # Prepare update data
            update_dict = item_data.model_dump(exclude_unset=True)
            
            # Update the item
            success = self.db.update_context_item(item_id, update_dict)
            if not success:
                return None
            
            # Return updated item
            return self.get_context_item(item_id)
            
        except Exception as e:
            logger.error(f"Failed to update context item {item_id}: {e}")
            return None
    
    def delete_context_item(self, item_id: int) -> bool:
        """Soft delete a context item"""
        try:
            return self.db.delete_context_item(item_id)
        except Exception as e:
            logger.error(f"Failed to delete context item {item_id}: {e}")
            return False
    
    def hard_delete_context_item(self, item_id: int) -> bool:
        """Hard delete a context item (permanently remove from database)"""
        try:
            return self.db.hard_delete_context_item(item_id)
        except Exception as e:
            logger.error(f"Failed to hard delete context item {item_id}: {e}")
            return False
    
    def search_context_items(self, search_query: ContextSearchQuery) -> ContextSearchResult:
        """Enhanced search with semantic, keyword, and hybrid options"""
        start_time = time.time()
        
        try:
            # Prepare filters
            filters = {"is_active": True}
            if search_query.project_id:
                filters["project_id"] = search_query.project_id
            if search_query.content_types:
                # For now, we'll filter after search since LanceDB doesn't support IN queries easily
                pass
            if search_query.tags:
                # For now, we'll filter after search since LanceDB doesn't support array contains easily
                pass
            
            # Perform search based on type
            if search_query.search_type == SearchType.SEMANTIC:
                results = self.db.semantic_search(
                    search_query.query, 
                    search_query.limit, 
                    filters
                )
            elif search_query.search_type == SearchType.KEYWORD:
                results = self.db.keyword_search(
                    search_query.query, 
                    search_query.limit, 
                    filters
                )
            else:  # HYBRID
                results = self.db.hybrid_search(
                    search_query.query, 
                    search_query.limit, 
                    search_query.semantic_weight,
                    filters
                )
            
            # Apply additional filters that couldn't be applied in the search
            if search_query.content_types:
                results = [r for r in results if r.get('content_type') in search_query.content_types]
            
            if search_query.tags:
                results = [r for r in results if any(tag in r.get('tags', []) for tag in search_query.tags)]
            
            # Apply pagination
            total = len(results)
            paginated_results = results[search_query.offset:search_query.offset + search_query.limit]
            
            # Convert to response objects
            items = []
            for result in paginated_results:
                items.append(ContextItemResponse(
                    id=result['id'],
                    title=result['title'],
                    content=result['content'],
                    content_type=result['content_type'],
                    tags=result['tags'],
                    extra_metadata=self._safe_json_parse(result.get('extra_metadata', {})),
                    source=result['source'],
                    project_id=result['project_id'],
                    is_active=result['is_active'],
                    created_at=self._safe_datetime_parse(result['created_at']),
                    updated_at=self._safe_datetime_parse(result.get('updated_at')),
                    combined_score=result.get('combined_score')
                ))
            
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            return ContextSearchResult(
                items=items,
                total=total,
                limit=search_query.limit,
                offset=search_query.offset,
                search_type=search_query.search_type,
                query=search_query.query,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"Failed to search context items: {e}")
            return ContextSearchResult(
                items=[],
                total=0,
                limit=search_query.limit,
                offset=search_query.offset,
                search_type=search_query.search_type,
                query=search_query.query,
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    # Project operations
    def create_project(self, project_data: ContextProjectCreate) -> ContextProjectResponse:
        """Create a new context project"""
        try:
            # Prepare data for insertion
            project_dict = project_data.model_dump()
            project_dict['is_active'] = True
            project_dict['created_at'] = datetime.now()
            project_dict['updated_at'] = None
            
            # Add to database
            self.db.add_project(project_dict)
            
            # Return response
            return ContextProjectResponse(
                id=project_data.id,
                name=project_data.name,
                description=project_data.description,
                settings=project_data.settings,
                is_active=True,
                created_at=project_dict['created_at'],
                updated_at=None
            )
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    def get_project(self, project_id: str) -> Optional[ContextProjectResponse]:
        """Get a project by ID"""
        try:
            project_data = self.db.get_project(project_id)
            if not project_data or not project_data.get('is_active', True):
                return None
            
            return ContextProjectResponse(
                id=project_data['id'],
                name=project_data['name'],
                description=project_data['description'],
                settings=self._safe_json_parse(project_data.get('settings', {})),
                is_active=project_data['is_active'],
                created_at=self._safe_datetime_parse(project_data['created_at']),
                updated_at=self._safe_datetime_parse(project_data.get('updated_at'))
            )
            
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            return None
    
    def get_projects(self, limit: int = 50, offset: int = 0) -> List[ContextProjectResponse]:
        """Get all active projects"""
        try:
            # Get all data from table
            results = self.db.projects_table.to_pandas()
            
            # Apply filters
            if not results.empty:
                # Filter by is_active
                results = results[results['is_active'] == True]
            
            # Apply offset and limit
            if offset > 0:
                results = results.iloc[offset:]
            if limit > 0:
                results = results.head(limit)
            
            # Convert to response objects
            projects = []
            for _, row in results.iterrows():
                projects.append(ContextProjectResponse(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    settings=self._safe_json_parse(row.get('settings', {})),
                    is_active=bool(row['is_active']),
                    created_at=self._safe_datetime_parse(row['created_at']),
                    updated_at=self._safe_datetime_parse(row.get('updated_at'))
                ))
            
            return projects
            
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []
    
    def update_project(self, project_id: str, project_data: ContextProjectUpdate) -> Optional[ContextProjectResponse]:
        """Update a project"""
        try:
            # Get existing project
            existing_project = self.get_project(project_id)
            if not existing_project:
                return None
            
            # Prepare update data
            update_dict = project_data.model_dump(exclude_unset=True)
            update_dict['updated_at'] = datetime.now()
            
            # Update the project (simplified - would need proper update method in LanceDB)
            # For now, we'll delete and recreate
            # This is a limitation of LanceDB - proper updates would need to be implemented
            
            return existing_project  # Placeholder - proper implementation needed
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            return None
    
    def delete_project(self, project_id: str) -> bool:
        """Soft delete a project"""
        try:
            # For now, we'll use hard delete since soft delete isn't fully implemented
            # This maintains consistency with the wipe functionality
            return self.db.hard_delete_project(project_id)
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            return False
    
    def hard_delete_project(self, project_id: str) -> bool:
        """Hard delete a project (permanently remove from database)"""
        try:
            return self.db.hard_delete_project(project_id)
        except Exception as e:
            logger.error(f"Failed to hard delete project {project_id}: {e}")
            return False
    
    # Statistics and analytics
    def get_context_stats(self, project_id: Optional[str] = None) -> ContextStats:
        """Get context statistics"""
        try:
            stats = self.db.get_table_stats()
            
            # Get additional stats
            all_items = self.db.context_table.to_pandas()
            active_items = all_items[all_items['is_active'] == True]
            
            if project_id:
                active_items = active_items[active_items['project_id'] == project_id]
            
            # Count by content type
            content_type_counts = active_items['content_type'].value_counts().to_dict()
            
            return ContextStats(
                total_items=len(active_items),  # Use active items count for total_items
                active_items=len(active_items),
                content_types=content_type_counts,
                projects_count=stats.get('projects_count', 0),
                embedding_dimension=stats.get('embedding_dimension', 0),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to get context stats: {e}")
            return ContextStats(
                total_items=0,
                active_items=0,
                content_types={},
                projects_count=0,
                embedding_dimension=0,
                last_updated=datetime.now()
            )
