"""Component model"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Component(Base):
    """Component model"""

    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    developer = Column(String(100))
    vcs_type = Column(String(20), default="git")  # git, svn, etc.
    vcs_url = Column(String(255))
    build_command = Column(String(255))
    component_url = Column(String(255))
    enabled = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="components")
    deployments = relationship("Deployment", back_populates="component", cascade="all, delete-orphan")

    __table_args__ = (
        # Ensure component name is unique per project
        # This would be a unique constraint on (project_id, name)
    )
