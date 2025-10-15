from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class SearchType(str, Enum):
    """Search type enumeration"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"

class ContextItemBase(BaseModel):
    """Base model for context items"""
    title: str = Field(..., description="Title of the context item")
    content: str = Field(..., description="Content of the context item")
    content_type: str = Field(default="text", description="Type of content")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    extra_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    source: Optional[str] = Field(None, description="Source of the context")
    project_id: Optional[str] = Field(None, description="Associated project ID")

class ContextItemCreate(ContextItemBase):
    """Model for creating context items"""
    pass

class ContextItemUpdate(BaseModel):
    """Model for updating context items"""
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    project_id: Optional[str] = None
    is_active: Optional[bool] = None

class ContextItemResponse(ContextItemBase):
    """Model for context item responses"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    combined_score: Optional[float] = Field(None, description="Search relevance score")
    
    class Config:
        from_attributes = True

class ContextProjectBase(BaseModel):
    """Base model for context projects"""
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project settings")

class ContextProjectCreate(ContextProjectBase):
    """Model for creating context projects"""
    pass

class ContextProjectUpdate(BaseModel):
    """Model for updating context projects"""
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ContextProjectResponse(ContextProjectBase):
    """Model for context project responses"""
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ContextSearchQuery(BaseModel):
    """Enhanced search query model with semantic search support"""
    query: str = Field(..., description="Search query")
    search_type: SearchType = Field(default=SearchType.HYBRID, description="Type of search to perform")
    content_types: Optional[List[str]] = Field(None, description="Filter by content types")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    project_id: Optional[str] = Field(None, description="Filter by project")
    limit: int = Field(default=50, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    semantic_weight: float = Field(default=0.7, ge=0.0, le=1.0, description="Weight for semantic search in hybrid mode")

class ContextSearchResult(BaseModel):
    """Enhanced search result model"""
    items: List[ContextItemResponse]
    total: int
    limit: int
    offset: int
    search_type: SearchType
    query: str
    execution_time_ms: Optional[float] = Field(None, description="Search execution time in milliseconds")

class ContextStats(BaseModel):
    """Context statistics model"""
    total_items: int
    active_items: int
    content_types: Dict[str, int]
    projects_count: int
    embedding_dimension: int
    last_updated: datetime

