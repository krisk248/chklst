"""Tests for Reports API endpoints"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.main import app
from backend.database import Base, get_db_session
from backend.models.deployment import Deployment
from backend.models.project import Project
from backend.models.component import Component


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio
    asyncio.run(setup_db())

    yield engine


@pytest.fixture
async def test_session(test_db):
    """Create test session"""
    async_session = sessionmaker(test_db, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def client(test_session):
    """Create test client"""
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db_session] = override_get_db
    return TestClient(app)


@pytest.fixture
async def sample_project(test_session):
    """Create a sample project"""
    project = Project(name="Test Project", description="Test project for reports")
    test_session.add(project)
    await test_session.flush()
    await test_session.refresh(project)
    return project


@pytest.fixture
async def sample_component(test_session, sample_project):
    """Create a sample component"""
    component = Component(
        name="Test Component",
        project_id=sample_project.id,
        description="Test component for reports"
    )
    test_session.add(component)
    await test_session.flush()
    await test_session.refresh(component)
    return component


@pytest.fixture
async def sample_deployments(test_session, sample_project, sample_component):
    """Create sample deployments"""
    deployments = [
        Deployment(
            jira_id="JIRA-001",
            project_id=sample_project.id,
            component_id=sample_component.id,
            environment="Production",
            vcs_url="https://git.example.com/repo",
            developer_name="John Doe",
            build_server="jenkins-1",
            deploy_server="deploy-1",
            timestamp=datetime(2025, 11, 9, 10, 30),
            build_status=True,
            deploy_status=True,
        ),
        Deployment(
            jira_id="JIRA-002",
            project_id=sample_project.id,
            component_id=sample_component.id,
            environment="Staging",
            vcs_url="https://git.example.com/repo",
            developer_name="Jane Smith",
            build_server="jenkins-1",
            deploy_server="deploy-2",
            timestamp=datetime(2025, 11, 10, 14, 15),
            build_status=True,
            deploy_status=False,
        ),
    ]

    for dep in deployments:
        test_session.add(dep)

    await test_session.flush()
    return deployments


class TestStatsEndpoint:
    """Tests for /stats endpoint"""

    @pytest.mark.asyncio
    async def test_stats_endpoint_with_valid_month(self, client, test_session, sample_deployments):
        """Test stats endpoint returns statistics"""
        response = client.get("/reports/stats?month=11&year=2025")

        assert response.status_code == 200
        data = response.json()

        assert "month" in data
        assert "year" in data
        assert "total" in data
        assert "successful" in data
        assert "failed" in data
        assert "success_rate" in data
        assert data["month"] == 11
        assert data["year"] == 2025

    @pytest.mark.asyncio
    async def test_stats_endpoint_invalid_month(self, client, test_session):
        """Test stats endpoint with invalid month"""
        response = client.get("/reports/stats?month=13&year=2025")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_stats_endpoint_invalid_year(self, client, test_session):
        """Test stats endpoint with invalid year"""
        response = client.get("/reports/stats?month=11&year=1999")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_stats_endpoint_empty_month(self, client, test_session):
        """Test stats endpoint with empty month returns zeros"""
        response = client.get("/reports/stats?month=12&year=2025")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 0
        assert data["successful"] == 0
        assert data["failed"] == 0


class TestPDFEndpoint:
    """Tests for /pdf endpoint"""

    @pytest.mark.asyncio
    async def test_pdf_endpoint_with_valid_month(self, client, test_session, sample_deployments):
        """Test PDF endpoint returns PDF file"""
        response = client.get("/reports/pdf?month=11&year=2025")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers.get("content-disposition", "")

        # Check that response contains PDF data
        content = response.content
        assert len(content) > 0
        assert content.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_pdf_endpoint_invalid_month(self, client, test_session):
        """Test PDF endpoint with invalid month"""
        response = client.get("/reports/pdf?month=13&year=2025")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_pdf_endpoint_invalid_year(self, client, test_session):
        """Test PDF endpoint with invalid year"""
        response = client.get("/reports/pdf?month=11&year=1999")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_pdf_endpoint_empty_month(self, client, test_session):
        """Test PDF endpoint with empty month"""
        response = client.get("/reports/pdf?month=12&year=2025")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

        # Should still generate a valid PDF even with no deployments
        content = response.content
        assert content.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_pdf_filename_format(self, client, test_session, sample_deployments):
        """Test PDF endpoint returns correct filename"""
        response = client.get("/reports/pdf?month=11&year=2025")

        assert response.status_code == 200
        content_disposition = response.headers.get("content-disposition", "")
        assert "November_2025" in content_disposition or "november_2025" in content_disposition.lower()


class TestExcelEndpoint:
    """Tests for /excel endpoint"""

    @pytest.mark.asyncio
    async def test_excel_endpoint_with_valid_month(self, client, test_session, sample_deployments):
        """Test Excel endpoint returns Excel file"""
        response = client.get("/reports/excel?month=11&year=2025")

        assert response.status_code == 200
        assert "spreadsheet" in response.headers.get("content-type", "")
        assert "attachment" in response.headers.get("content-disposition", "")

    @pytest.mark.asyncio
    async def test_excel_endpoint_invalid_month(self, client, test_session):
        """Test Excel endpoint with invalid month"""
        response = client.get("/reports/excel?month=13&year=2025")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_excel_endpoint_invalid_year(self, client, test_session):
        """Test Excel endpoint with invalid year"""
        response = client.get("/reports/excel?month=11&year=1999")
        assert response.status_code == 400
