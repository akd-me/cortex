from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

Base = declarative_base()

class ContextItem(Base):
    """SQLAlchemy model for context items"""
    __tablename__ = "context_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, code, markdown, json
    tags = Column(JSON, default=list)  # List of tags for categorization
    extra_metadata = Column(JSON, default=dict)  # Additional metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source = Column(String(255), nullable=True)  # Where this context came from
    project_id = Column(String(255), nullable=True, index=True)  # Project association

class ContextProject(Base):
    """SQLAlchemy model for context projects"""
    __tablename__ = "context_projects"
    
    id = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models for API
class ContextItemBase(BaseModel):
    title: str = Field(..., description="Title of the context item")
    content: str = Field(..., description="Content of the context item")
    content_type: str = Field(default="text", description="Type of content")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    extra_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    source: Optional[str] = Field(None, description="Source of the context")
    project_id: Optional[str] = Field(None, description="Associated project ID")

class ContextItemCreate(ContextItemBase):
    pass

class ContextItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    project_id: Optional[str] = None
    is_active: Optional[bool] = None

class ContextItemResponse(ContextItemBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ContextProjectBase(BaseModel):
    id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Project settings")

class ContextProjectCreate(ContextProjectBase):
    pass

class ContextProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ContextProjectResponse(ContextProjectBase):
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Search and query models
class ContextSearchQuery(BaseModel):
    query: str = Field(..., description="Search query")
    content_types: Optional[List[str]] = Field(None, description="Filter by content types")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    project_id: Optional[str] = Field(None, description="Filter by project")
    limit: int = Field(default=50, le=100, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")

class ContextSearchResult(BaseModel):
    items: List[ContextItemResponse]
    total: int
    limit: int
    offset: int
