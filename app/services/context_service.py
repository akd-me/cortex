from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from ..models.context import (
    ContextItem, ContextProject, 
    ContextItemCreate, ContextItemUpdate,
    ContextProjectCreate, ContextProjectUpdate,
    ContextSearchQuery
)

class ContextService:
    """Service layer for context management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Context Item operations
    def create_context_item(self, item_data: ContextItemCreate) -> ContextItem:
        """Create a new context item"""
        db_item = ContextItem(**item_data.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_context_item(self, item_id: int) -> Optional[ContextItem]:
        """Get a context item by ID"""
        return self.db.query(ContextItem).filter(
            and_(ContextItem.id == item_id, ContextItem.is_active == True)
        ).first()
    
    def get_context_items(
        self, 
        project_id: Optional[str] = None,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ContextItem]:
        """Get context items with optional filters"""
        query = self.db.query(ContextItem).filter(ContextItem.is_active == True)
        
        if project_id:
            query = query.filter(ContextItem.project_id == project_id)
        
        if content_type:
            query = query.filter(ContextItem.content_type == content_type)
        
        if tags:
            # Search for items that have any of the specified tags
            tag_conditions = [
                func.json_extract(ContextItem.tags, f'$[{i}]') == tag 
                for i, tag in enumerate(tags) for tag in tags
            ]
            query = query.filter(or_(*tag_conditions))
        
        return query.offset(offset).limit(limit).all()
    
    def update_context_item(self, item_id: int, item_data: ContextItemUpdate) -> Optional[ContextItem]:
        """Update a context item"""
        db_item = self.get_context_item(item_id)
        if not db_item:
            return None
        
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def delete_context_item(self, item_id: int) -> bool:
        """Soft delete a context item"""
        db_item = self.get_context_item(item_id)
        if not db_item:
            return False
        
        db_item.is_active = False
        self.db.commit()
        return True
    
    def search_context_items(self, search_query: ContextSearchQuery) -> tuple[List[ContextItem], int]:
        """Search context items with full-text search and filters"""
        query = self.db.query(ContextItem).filter(ContextItem.is_active == True)
        
        # Apply text search on title and content
        if search_query.query.strip():
            search_term = f"%{search_query.query}%"
            query = query.filter(
                or_(
                    ContextItem.title.ilike(search_term),
                    ContextItem.content.ilike(search_term)
                )
            )
        
        # Apply filters
        if search_query.content_types:
            query = query.filter(ContextItem.content_type.in_(search_query.content_types))
        
        if search_query.project_id:
            query = query.filter(ContextItem.project_id == search_query.project_id)
        
        if search_query.tags:
            # This is a simplified tag search - for production, consider using JSON operators
            tag_conditions = []
            for tag in search_query.tags:
                tag_conditions.append(ContextItem.tags.op('JSON_SEARCH')(tag, 'one', '$'))
            query = query.filter(or_(*tag_conditions))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        items = query.offset(search_query.offset).limit(search_query.limit).all()
        
        return items, total
    
    # Project operations
    def create_project(self, project_data: ContextProjectCreate) -> ContextProject:
        """Create a new context project"""
        db_project = ContextProject(**project_data.model_dump())
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def get_project(self, project_id: str) -> Optional[ContextProject]:
        """Get a project by ID"""
        return self.db.query(ContextProject).filter(
            and_(ContextProject.id == project_id, ContextProject.is_active == True)
        ).first()
    
    def get_projects(self, limit: int = 50, offset: int = 0) -> List[ContextProject]:
        """Get all active projects"""
        return self.db.query(ContextProject).filter(
            ContextProject.is_active == True
        ).offset(offset).limit(limit).all()
    
    def update_project(self, project_id: str, project_data: ContextProjectUpdate) -> Optional[ContextProject]:
        """Update a project"""
        db_project = self.get_project(project_id)
        if not db_project:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        self.db.commit()
        self.db.refresh(db_project)
        return db_project
    
    def delete_project(self, project_id: str) -> bool:
        """Soft delete a project"""
        db_project = self.get_project(project_id)
        if not db_project:
            return False
        
        db_project.is_active = False
        self.db.commit()
        return True
    
    # Statistics and analytics
    def get_context_stats(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get context statistics"""
        base_query = self.db.query(ContextItem).filter(ContextItem.is_active == True)
        
        if project_id:
            base_query = base_query.filter(ContextItem.project_id == project_id)
        
        total_items = base_query.count()
        
        # Count by content type
        content_type_stats = self.db.query(
            ContextItem.content_type, 
            func.count(ContextItem.id).label('count')
        ).filter(ContextItem.is_active == True)
        
        if project_id:
            content_type_stats = content_type_stats.filter(ContextItem.project_id == project_id)
        
        content_type_stats = content_type_stats.group_by(ContextItem.content_type).all()
        
        return {
            "total_items": total_items,
            "content_types": {stat[0]: stat[1] for stat in content_type_stats},
            "project_id": project_id
        }
