"""Application Settings model"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from backend.database import Base


class AppSettings(Base):
    """Application settings model"""

    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Common settings
    # deployed_by_default: boolean
    # excel_export_path: string
    # theme: string (light/dark)
    # auto_save_interval: integer
