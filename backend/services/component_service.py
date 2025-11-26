"""Component service for component management"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from backend.models.component import Component
from backend.models.project import Project
from backend.schemas.component import ComponentCreate, ComponentUpdate


async def add_component(
    session: AsyncSession,
    project_id: int,
    component: ComponentCreate
) -> Optional[Component]:
    """Add a component to a project"""
    # Verify project exists
    project_stmt = select(Project).where(Project.id == project_id)
    project_result = await session.execute(project_stmt)
    if not project_result.scalar_one_or_none():
        return None

    db_component = Component(
        project_id=project_id,
        name=component.name,
        developer=component.developer,
        vcs_type=component.vcs_type,
        vcs_url=component.vcs_url,
        build_command=component.build_command,
        component_url=component.component_url,
        enabled=component.enabled,
        description=component.description
    )

    session.add(db_component)
    await session.flush()
    await session.refresh(db_component)

    return db_component


async def get_component(
    session: AsyncSession,
    component_id: int
) -> Optional[Component]:
    """Get a component by ID"""
    stmt = select(Component).where(
        Component.id == component_id
    ).options(
        selectinload(Component.project)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_component(
    session: AsyncSession,
    component_id: int,
    component: ComponentUpdate
) -> Optional[Component]:
    """Update a component"""
    db_component = await get_component(session, component_id)

    if not db_component:
        return None

    # Update only provided fields
    update_data = component.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_component, field, value)

    db_component.updated_at = datetime.utcnow()

    session.add(db_component)
    await session.flush()
    await session.refresh(db_component)

    return db_component


async def delete_component(
    session: AsyncSession,
    component_id: int
) -> bool:
    """Delete a component"""
    db_component = await get_component(session, component_id)

    if not db_component:
        return False

    await session.delete(db_component)
    await session.flush()

    return True


async def get_project_components(
    session: AsyncSession,
    project_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Component]:
    """Get all components for a project"""
    stmt = select(Component).where(
        Component.project_id == project_id
    ).order_by(Component.name).offset(skip).limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_enabled_components(
    session: AsyncSession,
    project_id: int
) -> List[Component]:
    """Get all enabled components for a project"""
    stmt = select(Component).where(
        and_(
            Component.project_id == project_id,
            Component.enabled == True
        )
    ).order_by(Component.name)

    result = await session.execute(stmt)
    return result.scalars().all()


async def check_component_exists(
    session: AsyncSession,
    component_id: int
) -> bool:
    """Check if a component exists"""
    stmt = select(Component).where(Component.id == component_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def get_component_by_name(
    session: AsyncSession,
    project_id: int,
    name: str
) -> Optional[Component]:
    """Get a component by name within a project"""
    stmt = select(Component).where(
        and_(
            Component.project_id == project_id,
            Component.name == name
        )
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()
