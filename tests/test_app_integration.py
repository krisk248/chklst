"""
Integration tests for app.py and backend configuration.
Tests the complete startup flow and static file serving.
"""

import pytest
from pathlib import Path
from httpx import AsyncClient
import asyncio


@pytest.mark.asyncio
async def test_backend_app_creation():
    """Test that FastAPI app is created successfully"""
    from backend.main import app

    assert app is not None
    assert app.title == "chklst"


@pytest.mark.asyncio
async def test_backend_health_endpoint(test_async_client):
    """Test that health check endpoint works"""
    response = await test_async_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "chklst"


@pytest.mark.asyncio
async def test_backend_root_endpoint(test_async_client):
    """Test that root endpoint returns API info"""
    response = await test_async_client.get("/", follow_redirects=True)

    # Should return either API info or SPA fallback
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_backend_api_endpoints_exist(test_async_client):
    """Test that API endpoints are configured"""
    from backend.main import app

    # Check that API routers are included
    api_routes = [
        r for r in app.routes
        if hasattr(r, 'path') and r.path.startswith('/api/v1/')
    ]

    # Should have multiple API routes
    assert len(api_routes) > 0


@pytest.mark.asyncio
async def test_app_py_import():
    """Test that app.py module can be imported"""
    from app import main, run_production, run_development

    assert callable(main)
    assert callable(run_production)
    assert callable(run_development)


def test_frontend_dist_exists():
    """Test that frontend dist directory exists"""
    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
    assert frontend_dist.exists(), "Frontend dist directory must be built"


def test_frontend_index_html_exists():
    """Test that frontend index.html exists"""
    frontend_index = Path(__file__).parent.parent / "frontend" / "dist" / "index.html"
    assert frontend_index.exists(), "Frontend index.html must exist"


def test_frontend_assets_dir_exists():
    """Test that frontend assets directory exists"""
    frontend_assets = Path(__file__).parent.parent / "frontend" / "dist" / "assets"
    assert frontend_assets.exists(), "Frontend assets directory must exist"


def test_pipfile_has_dependencies():
    """Test that Pipfile has required dependencies"""
    pipfile = Path(__file__).parent.parent / "Pipfile"
    content = pipfile.read_text()

    # Check for key dependencies
    assert "fastapi" in content, "FastAPI not in Pipfile"
    assert "uvicorn" in content, "uvicorn not in Pipfile"
    assert "aiosqlite" in content, "aiosqlite not in Pipfile"


def test_build_sh_script_executable():
    """Test that build.sh is executable"""
    build_script = Path(__file__).parent.parent / "build.sh"
    import os
    assert os.access(build_script, os.X_OK), "build.sh is not executable"


def test_app_py_executable():
    """Test that app.py is executable"""
    app_py = Path(__file__).parent.parent / "app.py"
    import os
    assert os.access(app_py, os.X_OK), "app.py is not executable"


def test_app_py_has_shebang():
    """Test that app.py has proper shebang"""
    app_py = Path(__file__).parent.parent / "app.py"
    content = app_py.read_text()

    assert content.startswith("#!/usr/bin/env python3"), "app.py missing shebang"


def test_backend_main_static_file_mounting():
    """Test that backend mounts static files"""
    from backend.main import create_app

    app = create_app()

    # Check for static mount
    has_assets_mount = any(
        hasattr(r, 'path') and r.path == '/assets'
        for r in app.routes
    )

    assert has_assets_mount, "Static assets not mounted in backend"


def test_backend_main_spa_fallback_route():
    """Test that backend has SPA fallback route"""
    from backend.main import create_app

    app = create_app()

    # Check for SPA fallback route with {full_path:path}
    has_spa_fallback = any(
        hasattr(r, 'path') and '{full_path' in r.path
        for r in app.routes
    )

    assert has_spa_fallback, "SPA fallback route not configured"


@pytest.mark.asyncio
async def test_app_handles_missing_frontend_gracefully(test_async_client):
    """Test that app handles missing frontend gracefully"""
    # This tests the SPA fallback route
    response = await test_async_client.get("/nonexistent-route")

    # Should return either SPA fallback or error message
    assert response.status_code in [200, 404]
