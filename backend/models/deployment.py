"""Deployment model"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Deployment(Base):
    """Deployment record model"""

    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    jira_id = Column(String(50), index=True, nullable=True)  # Optional - can be empty
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=True)  # Nullable for legacy data
    environment = Column(String(50), nullable=True)
    vcs_url = Column(String(255))
    developer_name = Column(String(100))
    build_server = Column(String(100))
    deploy_server = Column(String(100))
    database_name = Column(String(100))
    db_backup_location = Column(String(255))
    database_script = Column(Text)
    previous_build_backup = Column(String(255))
    build_status = Column(String(50), default="pending")
    deploy_status = Column(String(50), default="pending")
    notes = Column(Text)
    deployed_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="deployments")
    component = relationship("Component", back_populates="deployments")
