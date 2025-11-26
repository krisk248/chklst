"""Settings API routes"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_db_session
from backend.services import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingResponse(BaseModel):
    """Setting response model"""
    key: str
    value: Any
    description: str = None

    class Config:
        from_attributes = True


class SettingCreate(BaseModel):
    """Setting create model"""
    value: Any
    description: str = None


@router.get("", response_model=Dict[str, Any])
async def get_settings(session: AsyncSession = Depends(get_db_session)):
    """Get all application settings as dictionary"""
    try:
        settings_dict = await settings_service.get_all_settings_as_dict(session)
        return settings_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get settings: {str(e)}"
        )


@router.post("", response_model=Dict[str, Any])
async def save_all_settings(
    data: Dict[str, Any],
    session: AsyncSession = Depends(get_db_session),
):
    """Save all settings at once"""
    try:
        for key, value in data.items():
            await settings_service.set_setting(session, key, value)
        await session.commit()
        return await settings_service.get_all_settings_as_dict(session)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save settings: {str(e)}"
        )


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a specific setting"""
    try:
        setting = await settings_service.get_setting(session, key)

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting with key '{key}' not found"
            )

        return setting
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get setting: {str(e)}"
        )


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    data: SettingCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update a specific setting"""
    try:
        setting = await settings_service.update_setting(
            session,
            key,
            data.value,
            data.description
        )

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setting with key '{key}' not found"
            )

        await session.commit()
        return setting
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update setting: {str(e)}"
        )


@router.post("/{key}", response_model=SettingResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    key: str,
    data: SettingCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new setting"""
    try:
        setting = await settings_service.set_setting(
            session,
            key,
            data.value,
            data.description
        )

        await session.commit()
        return setting
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create setting: {str(e)}"
        )
