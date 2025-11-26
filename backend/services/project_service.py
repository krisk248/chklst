"""Project service for CRUD operations"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.models.project import Project
from backend.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(
    session: AsyncSession,
    project: ProjectCreate
) -> Project:
    """Create a new project"""
    db_project = Project(
        name=project.name,
        build_server=project.build_server,
        deploy_server=project.deploy_server,
        database_name=project.database_name,
        environment=project.environment,
        backup_location=project.backup_location,
        description=project.description
    )

    session.add(db_project)
    await session.flush()
    await session.refresh(db_project)

    return db_project


async def get_project(
    session: AsyncSession,
    project_id: int
) -> Optional[Project]:
    """Get a project by ID"""
    stmt = select(Project).where(
        Project.id == project_id
    ).options(
        selectinload(Project.components),
        selectinload(Project.deployments)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_projects(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Project]:
    """Get all projects"""
    stmt = select(Project).options(
        selectinload(Project.components)
    ).order_by(desc(Project.created_at)).offset(skip).limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()


async def update_project(
    session: AsyncSession,
    project_id: int,
    project: ProjectUpdate
) -> Optional[Project]:
    """Update a project"""
    db_project = await get_project(session, project_id)

    if not db_project:
        return None

    # Update only provided fields
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    db_project.updated_at = datetime.utcnow()

    session.add(db_project)
    await session.flush()
    await session.refresh(db_project)

    return db_project


async def delete_project(
    session: AsyncSession,
    project_id: int
) -> bool:
    """Delete a project (cascades to components and deployments)"""
    db_project = await get_project(session, project_id)

    if not db_project:
        return False

    await session.delete(db_project)
    await session.flush()

    return True


async def get_project_by_name(
    session: AsyncSession,
    name: str
) -> Optional[Project]:
    """Get a project by name"""
    stmt = select(Project).where(
        Project.name == name
    ).options(
        selectinload(Project.components)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def copy_project(
    session: AsyncSession,
    project_id: int,
    new_name: str
) -> Optional[Project]:
    """Copy a project with a new name"""
    original_project = await get_project(session, project_id)

    if not original_project:
        return None

    # Check if new name already exists
    existing = await get_project_by_name(session, new_name)
    if existing:
        return None

    # Create new project with copied data
    new_project = Project(
        name=new_name,
        build_server=original_project.build_server,
        deploy_server=original_project.deploy_server,
        database_name=original_project.database_name,
        environment=original_project.environment,
        backup_location=original_project.backup_location,
        description=original_project.description
    )

    session.add(new_project)
    await session.flush()
    await session.refresh(new_project)

    return new_project


async def check_project_exists(
    session: AsyncSession,
    project_id: int
) -> bool:
    """Check if a project exists"""
    stmt = select(Project).where(Project.id == project_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None
