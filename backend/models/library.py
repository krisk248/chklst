"""Library/Presets model"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from backend.database import Base


class Library(Base):
    """Library/Presets for commonly used values"""

    __tablename__ = "library"

    id = Column(Integer, primary_key=True, index=True)
    developers = Column(JSON, default=list)
    build_servers = Column(JSON, default=list)
    deploy_servers = Column(JSON, default=list)
    environments = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, id=None, developers=None, build_servers=None, deploy_servers=None, environments=None):
        """Initialize with default or provided values"""
        super().__init__()
        if id is not None:
            self.id = id
        self.developers = developers if developers is not None else ["Kannan"]
        self.build_servers = build_servers if build_servers is not None else ["192.168.1.149"]
        self.deploy_servers = deploy_servers if deploy_servers is not None else []
        self.environments = environments if environments is not None else ["QA", "UAT", "Production"]
