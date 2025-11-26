"""Deployments API routes"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session
from backend.schemas import (
    DeploymentCreate,
    DeploymentUpdate,
    DeploymentResponse,
    DeploymentListResponse,
)
from backend.services import deployment_service
from backend.websocket.manager import manager

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.get("", response_model=List[DeploymentListResponse])
async def list_deployments(
    skip: int = 0,
    limit: int = 1000,
    project_id: int = None,
    month: int = None,
    year: int = None,
    session: AsyncSession = Depends(get_db_session),
):
    """List deployments with optional filtering by project, month and year"""
    try:
        deployments = await deployment_service.get_deployments(
            session,
            project_id=project_id,
            month=month,
            year=year,
            skip=skip,
            limit=limit
        )
        return deployments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list deployments: {str(e)}"
        )


@router.post("", response_model=DeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_deployment(
    deployment: DeploymentCreate,
    session: AsyncSession = Depends(get_db_session),
):
    """Create a new deployment with duplicate checking"""
    try:
        # Check for duplicates
        is_duplicate, details = await deployment_service.check_duplicate(session, deployment)
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=details
            )

        db_deployment = await deployment_service.create_deployment(session, deployment)
        await session.commit()

        # WebSocket disabled for single-user app
        # await manager.broadcast_deployment_created(...)

        return db_deployment
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deployment: {str(e)}"
        )


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Get deployment by ID"""
    try:
        db_deployment = await deployment_service.get_deployment(session, deployment_id)

        if not db_deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {deployment_id} not found"
            )

        return db_deployment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment: {str(e)}"
        )


@router.put("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: int,
    deployment: DeploymentUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update a deployment"""
    try:
        db_deployment = await deployment_service.update_deployment(
            session,
            deployment_id,
            deployment
        )

        if not db_deployment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {deployment_id} not found"
            )

        await session.commit()

        # WebSocket disabled for single-user app
        # await manager.broadcast_deployment_updated(...)

        return db_deployment
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update deployment: {str(e)}"
        )


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(
    deployment_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    """Delete a deployment"""
    try:
        deleted = await deployment_service.delete_deployment(session, deployment_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {deployment_id} not found"
            )

        await session.commit()
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete deployment: {str(e)}"
        )


@router.get("/project/{project_id}", response_model=List[DeploymentListResponse])
async def get_project_deployments(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """Get all deployments for a project"""
    try:
        deployments = await deployment_service.get_project_deployments(
            session,
            project_id,
            skip=skip,
            limit=limit
        )
        return deployments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project deployments: {str(e)}"
        )
