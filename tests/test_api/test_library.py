"""Tests for Library API"""

import pytest


@pytest.mark.asyncio
async def test_get_library(test_async_client):
    """Test getting library"""
    response = await test_async_client.get("/api/v1/library")

    # TODO: Implement endpoint
    # assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_developer(test_async_client):
    """Test adding a developer"""
    developer_data = {
        "name": "John Doe",
    }

    response = await test_async_client.post(
        "/api/v1/library/developers",
        json=developer_data,
    )

    # TODO: Implement endpoint
    # assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_remove_developer(test_async_client):
    """Test removing a developer"""
    response = await test_async_client.delete("/api/v1/library/developers/John")

    # TODO: Implement endpoint
    # assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_build_server(test_async_client):
    """Test adding a build server"""
    server_data = {
        "name": "build-server.local",
    }

    response = await test_async_client.post(
        "/api/v1/library/build-servers",
        json=server_data,
    )

    # TODO: Implement endpoint
    # assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_add_environment(test_async_client):
    """Test adding an environment"""
    env_data = {
        "name": "Staging",
    }

    response = await test_async_client.post(
        "/api/v1/library/environments",
        json=env_data,
    )

    # TODO: Implement endpoint
    # assert response.status_code in [200, 201]
