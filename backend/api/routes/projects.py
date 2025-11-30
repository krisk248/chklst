"""Projects API routes"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session
from backend.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from backend.schemas.component import ComponentCreate, ComponentUpdate, ComponentResponse
from backend.services import project_service
from backend.services import component_service
from backend.websocket.manager import manager

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
):
    """List all projects with components"""
    try:
        projects = await project_service.get_all_projects(session, skip=skip, limit=limit)
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new project"""
    try:
        db_project = await project_service.create_project(session, project)
        await session.commit()
        return db_project
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get project by ID"""
    try:
        db_project = await project_service.get_project(session, project_id)

        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )

        return db_project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update a project"""
    try:
        db_project = await project_service.update_project(session, project_id, project)

        if not db_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )

        await session.commit()

        # Broadcast WebSocket message to all connected clients
        await manager.broadcast_project_updated({"id": db_project.id, "name": db_project.name})

        return db_project
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a project"""
    try:
        deleted = await project_service.delete_project(session, project_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )

        await session.commit()
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


# ============== Component Routes ==============

@router.post("/{project_id}/components", response_model=ComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_component(
    project_id: int,
    component: ComponentCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new component for a project"""
    try:
        # Override project_id from URL
        component.project_id = project_id

        db_component = await component_service.add_component(session, project_id, component)

        if not db_component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )

        await session.commit()

        # Broadcast update
        await manager.broadcast_project_updated({"project_id": project_id, "component_created": db_component.id})

        return db_component
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create component: {str(e)}"
        )


@router.get("/{project_id}/components/{component_id}", response_model=ComponentResponse)
async def get_component(
    project_id: int,
    component_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get a specific component"""
    try:
        db_component = await component_service.get_component(session, component_id)

        if not db_component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component with ID {component_id} not found"
            )

        if db_component.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Component {component_id} does not belong to project {project_id}"
            )

        return db_component
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get component: {str(e)}"
        )


@router.put("/{project_id}/components/{component_id}", response_model=ComponentResponse)
async def update_component(
    project_id: int,
    component_id: int,
    component: ComponentUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update a component within a project"""
    try:
        # Verify component belongs to the project
        existing = await component_service.get_component(session, component_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component with ID {component_id} not found"
            )
        if existing.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Component {component_id} does not belong to project {project_id}"
            )

        db_component = await component_service.update_component(session, component_id, component)
        await session.commit()

        # Broadcast update
        await manager.broadcast_project_updated({"project_id": project_id, "component_updated": component_id})

        return db_component
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update component: {str(e)}"
        )


@router.delete("/{project_id}/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(
    project_id: int,
    component_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a component from a project"""
    try:
        # Verify component belongs to the project
        existing = await component_service.get_component(session, component_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component with ID {component_id} not found"
            )
        if existing.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Component {component_id} does not belong to project {project_id}"
            )

        deleted = await component_service.delete_component(session, component_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component with ID {component_id} not found"
            )

        await session.commit()

        # Broadcast update
        await manager.broadcast_project_updated({"project_id": project_id, "component_deleted": component_id})

    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete component: {str(e)}"
        )
