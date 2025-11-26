"""Settings service for app settings management"""

from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.settings import AppSettings


async def get_settings(session: AsyncSession) -> List[AppSettings]:
    """Get all application settings"""
    stmt = select(AppSettings)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_setting(
    session: AsyncSession,
    key: str
) -> Optional[AppSettings]:
    """Get a specific setting by key"""
    stmt = select(AppSettings).where(AppSettings.key == key)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_setting_value(
    session: AsyncSession,
    key: str,
    default: Any = None
) -> Any:
    """Get setting value with optional default"""
    setting = await get_setting(session, key)
    if setting:
        return setting.value
    return default


async def set_setting(
    session: AsyncSession,
    key: str,
    value: Any,
    description: Optional[str] = None
) -> AppSettings:
    """Set a setting (create or update)"""
    setting = await get_setting(session, key)

    if setting:
        setting.value = value
        if description is not None:
            setting.description = description
    else:
        setting = AppSettings(
            key=key,
            value=value,
            description=description
        )
        session.add(setting)

    await session.flush()
    await session.refresh(setting)

    return setting


async def update_setting(
    session: AsyncSession,
    key: str,
    value: Any,
    description: Optional[str] = None
) -> Optional[AppSettings]:
    """Update a setting"""
    setting = await get_setting(session, key)

    if not setting:
        return None

    setting.value = value
    if description is not None:
        setting.description = description

    session.add(setting)
    await session.flush()
    await session.refresh(setting)

    return setting


async def delete_setting(
    session: AsyncSession,
    key: str
) -> bool:
    """Delete a setting"""
    setting = await get_setting(session, key)

    if not setting:
        return False

    await session.delete(setting)
    await session.flush()

    return True


async def get_all_settings_as_dict(session: AsyncSession) -> Dict[str, Any]:
    """Get all settings as a dictionary"""
    settings = await get_settings(session)
    return {setting.key: setting.value for setting in settings}


async def bulk_set_settings(
    session: AsyncSession,
    settings_dict: Dict[str, Any]
) -> List[AppSettings]:
    """Bulk set multiple settings"""
    results = []

    for key, value in settings_dict.items():
        setting = await set_setting(session, key, value)
        results.append(setting)

    return results
