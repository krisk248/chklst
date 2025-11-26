"""Deployment service for CRUD operations"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, extract
from sqlalchemy.orm import selectinload

from backend.models.deployment import Deployment
from backend.models.project import Project
from backend.models.component import Component
from backend.schemas.deployment import DeploymentCreate, DeploymentUpdate
from backend.websocket.manager import manager


async def create_deployment(
    session: AsyncSession,
    deployment: DeploymentCreate
) -> Deployment:
    """Create a new deployment record"""
    db_deployment = Deployment(
        jira_id=deployment.jira_id,
        project_id=deployment.project_id,
        component_id=deployment.component_id,
        environment=deployment.environment,
        vcs_url=deployment.vcs_url,
        developer_name=deployment.developer_name,
        build_server=deployment.build_server,
        deploy_server=deployment.deploy_server,
        database_name=deployment.database_name,
        db_backup_location=deployment.db_backup_location,
        database_script=deployment.database_script,
        previous_build_backup=deployment.previous_build_backup,
        build_status=deployment.build_status,
        deploy_status=deployment.deploy_status,
        notes=deployment.notes,
        deployed_by=deployment.deployed_by,
        timestamp=deployment.timestamp or datetime.utcnow()
    )

    session.add(db_deployment)
    await session.flush()
    await session.refresh(db_deployment)

    return db_deployment


async def get_deployment(
    session: AsyncSession,
    deployment_id: int
) -> Optional[Deployment]:
    """Get a deployment by ID"""
    stmt = select(Deployment).where(
        Deployment.id == deployment_id
    ).options(
        selectinload(Deployment.project),
        selectinload(Deployment.component)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_deployments(
    session: AsyncSession,
    project_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Deployment]:
    """Get deployments with optional filtering"""
    filters = []

    if project_id is not None:
        filters.append(Deployment.project_id == project_id)

    if month is not None and year is not None:
        filters.append(
            and_(
                extract('month', Deployment.timestamp) == month,
                extract('year', Deployment.timestamp) == year
            )
        )

    stmt = select(Deployment).options(
        selectinload(Deployment.project),
        selectinload(Deployment.component)
    )

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.order_by(desc(Deployment.timestamp)).offset(skip).limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()


async def update_deployment(
    session: AsyncSession,
    deployment_id: int,
    deployment: DeploymentUpdate
) -> Optional[Deployment]:
    """Update a deployment"""
    db_deployment = await get_deployment(session, deployment_id)

    if not db_deployment:
        return None

    # Update only provided fields
    update_data = deployment.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_deployment, field, value)

    db_deployment.updated_at = datetime.utcnow()

    session.add(db_deployment)
    await session.flush()
    await session.refresh(db_deployment)

    return db_deployment


async def delete_deployment(
    session: AsyncSession,
    deployment_id: int
) -> bool:
    """Delete a deployment"""
    db_deployment = await get_deployment(session, deployment_id)

    if not db_deployment:
        return False

    await session.delete(db_deployment)
    await session.flush()

    return True


async def check_duplicate(
    session: AsyncSession,
    deployment: DeploymentCreate
) -> Tuple[bool, Optional[str]]:
    """Check if deployment is duplicate - same jira_id for same component is not allowed"""
    # Skip check if jira_id is empty/null - allow deployments without patch ID
    if not deployment.jira_id or deployment.jira_id.strip() == "":
        return False, None

    # Check ALL records for same component with same jira_id
    stmt = select(Deployment).where(
        and_(
            Deployment.component_id == deployment.component_id,
            Deployment.jira_id == deployment.jira_id.strip()
        )
    )

    result = await session.execute(stmt)
    existing = result.scalars().first()

    if existing:
        return True, f"Patch ID '{deployment.jira_id}' already exists for this component"

    return False, None


async def get_monthly_deployments(
    session: AsyncSession,
    month: int,
    year: int
) -> List[Deployment]:
    """Get all deployments for a specific month"""
    stmt = select(Deployment).where(
        and_(
            extract('month', Deployment.timestamp) == month,
            extract('year', Deployment.timestamp) == year
        )
    ).options(
        selectinload(Deployment.project),
        selectinload(Deployment.component)
    ).order_by(desc(Deployment.timestamp))

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_deployment_stats(
    session: AsyncSession,
    month: int,
    year: int
) -> Dict[str, Any]:
    """Get deployment statistics for a month"""
    deployments = await get_monthly_deployments(session, month, year)

    total_deployments = len(deployments)
    successful_deployments = sum(
        1 for d in deployments
        if d.deploy_status == "success" or d.deploy_status == "completed"
    )
    failed_deployments = total_deployments - successful_deployments

    # Count by environment
    by_environment = {}
    for d in deployments:
        env = d.environment or "Unknown"
        by_environment[env] = by_environment.get(env, 0) + 1

    # Count by project
    by_project = {}
    for d in deployments:
        project_name = d.project.name if d.project else "Unknown"
        by_project[project_name] = by_project.get(project_name, 0) + 1

    return {
        "total_deployments": total_deployments,
        "successful_deployments": successful_deployments,
        "failed_deployments": failed_deployments,
        "success_rate": (successful_deployments / total_deployments * 100) if total_deployments > 0 else 0,
        "by_environment": by_environment,
        "by_project": by_project,
        "month": month,
        "year": year
    }


async def get_project_deployments(
    session: AsyncSession,
    project_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Deployment]:
    """Get all deployments for a project"""
    return await get_deployments(
        session,
        project_id=project_id,
        skip=skip,
        limit=limit
    )
