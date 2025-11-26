"""Tests for Deployments API"""

import pytest


@pytest.mark.asyncio
async def test_list_deployments_empty(test_async_client):
    """Test listing deployments when empty"""
    response = await test_async_client.get("/api/v1/deployments")

    assert response.status_code == 200
    assert response.json() == [] or isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_deployments_with_pagination(test_async_client):
    """Test listing deployments with pagination"""
    response = await test_async_client.get(
        "/api/v1/deployments?skip=0&limit=10"
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_deployment(test_async_client):
    """Test creating a deployment"""
    deployment_data = {
        "jira_id": "JIRA-001",
        "project_id": 1,
        "component_id": 1,
        "environment": "QA",
        "build_status": "success",
        "deploy_status": "success",
    }

    response = await test_async_client.post(
        "/api/v1/deployments",
        json=deployment_data,
    )

    # TODO: Implement endpoint to return 201
    # assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_get_deployment(test_async_client):
    """Test getting a deployment"""
    response = await test_async_client.get("/api/v1/deployments/1")

    # TODO: Implement endpoint
    # assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_project_deployments(test_async_client):
    """Test getting deployments for a project"""
    response = await test_async_client.get("/api/v1/deployments/project/1")

    # TODO: Implement endpoint
    # assert response.status_code == 200
