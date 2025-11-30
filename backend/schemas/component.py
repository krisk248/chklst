"""Component schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ComponentBase(BaseModel):
    """Base component schema"""
    name: str = Field(..., min_length=1, max_length=100)
    developer: Optional[str] = None
    vcs_type: Optional[str] = "git"
    vcs_url: Optional[str] = None
    build_command: Optional[str] = None
    component_url: Optional[str] = None
    enabled: Optional[bool] = True
    description: Optional[str] = None


class ComponentCreate(ComponentBase):
    """Create component schema"""
    project_id: Optional[int] = None  # Set from URL parameter


class ComponentUpdate(BaseModel):
    """Update component schema"""
    name: Optional[str] = None
    developer: Optional[str] = None
    vcs_type: Optional[str] = None
    vcs_url: Optional[str] = None
    build_command: Optional[str] = None
    component_url: Optional[str] = None
    enabled: Optional[bool] = None
    description: Optional[str] = None


class ComponentResponse(ComponentBase):
    """Component response schema"""
    id: int
    project_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComponentListResponse(BaseModel):
    """Component list response"""
    id: int
    name: str
    developer: Optional[str] = None
    enabled: Optional[bool] = True

    class Config:
        from_attributes = True
