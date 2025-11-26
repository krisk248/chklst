"""Tests for health check and root endpoints"""

import pytest


@pytest.mark.asyncio
async def test_health_check(test_async_client):
    """Test health check endpoint"""
    response = await test_async_client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(test_async_client):
    """Test root endpoint"""
    response = await test_async_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "api_version" in data
