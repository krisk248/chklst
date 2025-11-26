"""Library/Presets API routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db_session
from backend.schemas import (
    LibraryResponse,
    LibraryUpdate,
    DeveloperAdd,
    ServerAdd,
    EnvironmentAdd,
    ItemRemove,
)
from backend.services import library_service
from backend.websocket.manager import manager

router = APIRouter(prefix="/library", tags=["library"])


@router.get("", response_model=LibraryResponse)
async def get_library(session: AsyncSession = Depends(get_db_session)):
    """Get library/presets"""
    try:
        library = await library_service.get_library(session)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get library"
            )

        await session.commit()
        return library
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get library: {str(e)}"
        )


@router.put("", response_model=LibraryResponse)
async def update_library(
    library: LibraryUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """Update entire library"""
    try:
        updated_library = await library_service.update_library(
            session,
            developers=library.developers,
            build_servers=library.build_servers,
            deploy_servers=library.deploy_servers,
            environments=library.environments
        )

        if not updated_library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update library"
            )

        await session.commit()

        # Broadcast WebSocket message to all connected clients
        await manager.broadcast_library_updated()

        return updated_library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update library: {str(e)}"
        )


@router.post("/developers", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def add_developer(
    developer: DeveloperAdd,
    session: AsyncSession = Depends(get_db_session),
):
    """Add a developer to library"""
    try:
        library = await library_service.add_developer(session, developer.name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add developer"
            )

        await session.commit()

        # Broadcast WebSocket message to all connected clients
        await manager.broadcast_library_updated()

        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add developer: {str(e)}"
        )


@router.delete("/developers/{name}", response_model=LibraryResponse)
async def remove_developer(
    name: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Remove a developer from library"""
    try:
        library = await library_service.remove_developer(session, name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove developer"
            )

        await session.commit()
        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove developer: {str(e)}"
        )


@router.post("/build-servers", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def add_build_server(
    server: ServerAdd,
    session: AsyncSession = Depends(get_db_session),
):
    """Add a build server to library"""
    try:
        library = await library_service.add_build_server(session, server.name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add build server"
            )

        await session.commit()
        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add build server: {str(e)}"
        )


@router.delete("/build-servers/{name}", response_model=LibraryResponse)
async def remove_build_server(
    name: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Remove a build server from library"""
    try:
        library = await library_service.remove_build_server(session, name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove build server"
            )

        await session.commit()
        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove build server: {str(e)}"
        )


@router.post("/deploy-servers", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def add_deploy_server(
    server: ServerAdd,
    session: AsyncSession = Depends(get_db_session),
):
    """Add a deploy server to library"""
    try:
        library = await library_service.add_deploy_server(session, server.name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add deploy server"
            )

        await session.commit()
        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add deploy server: {str(e)}"
        )


@router.delete("/deploy-servers/{name}", response_model=LibraryResponse)
async def remove_deploy_server(
    name: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Remove a deploy server from library"""
    try:
        library = await library_service.remove_deploy_server(session, name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove deploy server"
            )

        await session.commit()
        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove deploy server: {str(e)}"
        )


@router.post("/environments", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def add_environment(
    environment: EnvironmentAdd,
    session: AsyncSession = Depends(get_db_session),
):
    """Add an environment to library"""
    try:
        library = await library_service.add_environment(session, environment.name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add environment"
            )

        await session.commit()
        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add environment: {str(e)}"
        )


@router.delete("/environments/{name}", response_model=LibraryResponse)
async def remove_environment(
    name: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Remove an environment from library"""
    try:
        library = await library_service.remove_environment(session, name)

        if not library:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove environment"
            )

        await session.commit()
        return library
    except HTTPException:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove environment: {str(e)}"
        )
