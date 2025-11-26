"""Library service for library/presets management"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.library import Library


async def get_library(session: AsyncSession) -> Optional[Library]:
    """Get the library record (should be singleton)"""
    stmt = select(Library).limit(1)
    result = await session.execute(stmt)
    library = result.scalar_one_or_none()

    # If no library exists, create default one
    if not library:
        library = Library()
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def add_developer(
    session: AsyncSession,
    name: str
) -> Optional[Library]:
    """Add a developer to the library"""
    library = await get_library(session)

    if not library:
        return None

    if name not in library.developers:
        library.developers.append(name)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def remove_developer(
    session: AsyncSession,
    name: str
) -> Optional[Library]:
    """Remove a developer from the library"""
    library = await get_library(session)

    if not library:
        return None

    if name in library.developers:
        library.developers.remove(name)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def add_build_server(
    session: AsyncSession,
    server: str
) -> Optional[Library]:
    """Add a build server to the library"""
    library = await get_library(session)

    if not library:
        return None

    if server not in library.build_servers:
        library.build_servers.append(server)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def remove_build_server(
    session: AsyncSession,
    server: str
) -> Optional[Library]:
    """Remove a build server from the library"""
    library = await get_library(session)

    if not library:
        return None

    if server in library.build_servers:
        library.build_servers.remove(server)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def add_deploy_server(
    session: AsyncSession,
    server: str
) -> Optional[Library]:
    """Add a deploy server to the library"""
    library = await get_library(session)

    if not library:
        return None

    if server not in library.deploy_servers:
        library.deploy_servers.append(server)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def remove_deploy_server(
    session: AsyncSession,
    server: str
) -> Optional[Library]:
    """Remove a deploy server from the library"""
    library = await get_library(session)

    if not library:
        return None

    if server in library.deploy_servers:
        library.deploy_servers.remove(server)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def add_environment(
    session: AsyncSession,
    environment: str
) -> Optional[Library]:
    """Add an environment to the library"""
    library = await get_library(session)

    if not library:
        return None

    if environment not in library.environments:
        library.environments.append(environment)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def remove_environment(
    session: AsyncSession,
    environment: str
) -> Optional[Library]:
    """Remove an environment from the library"""
    library = await get_library(session)

    if not library:
        return None

    if environment in library.environments:
        library.environments.remove(environment)
        session.add(library)
        await session.flush()
        await session.refresh(library)

    return library


async def update_library(
    session: AsyncSession,
    developers: List[str],
    build_servers: List[str],
    deploy_servers: List[str],
    environments: List[str]
) -> Optional[Library]:
    """Update entire library"""
    library = await get_library(session)

    if not library:
        return None

    library.developers = developers
    library.build_servers = build_servers
    library.deploy_servers = deploy_servers
    library.environments = environments

    session.add(library)
    await session.flush()
    await session.refresh(library)

    return library
