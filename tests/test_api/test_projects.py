"""Tests for Projects API"""

import pytest


@pytest.mark.asyncio
async def test_list_projects_empty(test_async_client):
    """Test listing projects when empty"""
    response = await test_async_client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == [] or isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_project(test_async_client):
    """Test creating a project"""
    project_data = {
        "name": "Test Project",
        "build_server": "build-server.local",
        "deploy_server": "deploy-server.local",
        "database_name": "test_db",
        "environment": "QA",
        "description": "Test project for deployment tracking",
    }

    response = await test_async_client.post(
        "/api/v1/projects",
        json=project_data,
    )

    # TODO: Implement endpoint to return 201
    # assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_get_project(test_async_client):
    """Test getting a project"""
    response = await test_async_client.get("/api/v1/projects/1")

    # TODO: Implement endpoint
    # assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_project(test_async_client):
    """Test updating a project"""
    update_data = {
        "name": "Updated Project",
    }

    response = await test_async_client.put(
        "/api/v1/projects/1",
        json=update_data,
    )

    # TODO: Implement endpoint
    # assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_project(test_async_client):
    """Test deleting a project"""
    response = await test_async_client.delete("/api/v1/projects/1")

    # TODO: Implement endpoint
    # assert response.status_code == 204
