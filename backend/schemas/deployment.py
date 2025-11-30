"""Deployment schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DeploymentBase(BaseModel):
    """Base deployment schema"""
    jira_id: Optional[str] = Field(None, max_length=50)  # Optional - can be empty
    project_id: int
    component_id: Optional[int] = None  # Nullable for legacy data
    environment: Optional[str] = None
    vcs_url: Optional[str] = None
    developer_name: Optional[str] = None
    build_server: Optional[str] = None
    deploy_server: Optional[str] = None
    database_name: Optional[str] = None
    db_backup_location: Optional[str] = None
    database_script: Optional[str] = None
    previous_build_backup: Optional[str] = None
    build_status: str = "pending"
    deploy_status: str = "pending"
    notes: Optional[str] = None
    deployed_by: Optional[str] = None


class DeploymentCreate(DeploymentBase):
    """Create deployment schema"""
    timestamp: Optional[datetime] = None


class DeploymentUpdate(BaseModel):
    """Update deployment schema"""
    jira_id: Optional[str] = None
    environment: Optional[str] = None
    vcs_url: Optional[str] = None
    developer_name: Optional[str] = None
    build_server: Optional[str] = None
    deploy_server: Optional[str] = None
    database_name: Optional[str] = None
    db_backup_location: Optional[str] = None
    database_script: Optional[str] = None
    previous_build_backup: Optional[str] = None
    build_status: Optional[str] = None
    deploy_status: Optional[str] = None
    notes: Optional[str] = None
    deployed_by: Optional[str] = None


class DeploymentResponse(DeploymentBase):
    """Deployment response schema"""
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeploymentListResponse(BaseModel):
    """Deployment list response"""
    id: int
    jira_id: Optional[str] = None
    timestamp: datetime
    project_id: int
    component_id: Optional[int] = None  # Nullable for legacy data
    environment: Optional[str] = None
    vcs_url: Optional[str] = None
    build_server: Optional[str] = None
    deploy_server: Optional[str] = None
    database_name: Optional[str] = None
    database_script: Optional[str] = None
    deploy_status: str
    deployed_by: Optional[str] = None
    developer_name: Optional[str] = None
    build_status: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True
