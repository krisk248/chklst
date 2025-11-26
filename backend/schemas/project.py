"""Project schemas"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ComponentInProject(BaseModel):
    """Component nested in project"""
    id: int
    name: str
    developer: Optional[str] = None
    vcs_type: Optional[str] = "git"
    vcs_url: Optional[str] = None
    build_command: Optional[str] = None
    component_url: Optional[str] = None
    enabled: Optional[bool] = True

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=100)
    build_server: Optional[str] = None
    deploy_server: Optional[str] = None
    database_name: Optional[str] = None
    environment: Optional[str] = None
    backup_location: Optional[str] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Create project schema"""
    pass


class ProjectUpdate(BaseModel):
    """Update project schema"""
    name: Optional[str] = None
    build_server: Optional[str] = None
    deploy_server: Optional[str] = None
    database_name: Optional[str] = None
    environment: Optional[str] = None
    backup_location: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    components: List[ComponentInProject] = []

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Project list response"""
    id: int
    name: str
    environment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
