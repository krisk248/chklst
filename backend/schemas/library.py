"""Library schemas"""

from datetime import datetime
from typing import List
from pydantic import BaseModel


class LibraryResponse(BaseModel):
    """Library response schema"""
    id: int
    developers: List[str]
    build_servers: List[str]
    deploy_servers: List[str]
    environments: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LibraryUpdate(BaseModel):
    """Library update schema"""
    developers: List[str]
    build_servers: List[str]
    deploy_servers: List[str]
    environments: List[str]


class DeveloperAdd(BaseModel):
    """Add developer schema"""
    name: str


class ServerAdd(BaseModel):
    """Add server schema"""
    name: str


class EnvironmentAdd(BaseModel):
    """Add environment schema"""
    name: str


class ItemRemove(BaseModel):
    """Remove item schema"""
    name: str
