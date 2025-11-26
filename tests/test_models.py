"""Tests for SQLAlchemy models"""

import pytest
from datetime import datetime

from backend.models import Project, Component, Deployment, Library, AppSettings


@pytest.mark.asyncio
async def test_project_creation(db_session):
    """Test creating a project"""
    project = Project(
        name="Test Project",
        build_server="build-server.local",
        deploy_server="deploy-server.local",
        database_name="test_db",
        environment="QA",
    )

    db_session.add(project)
    await db_session.commit()

    # Verify project was created
    assert project.id is not None
    assert project.name == "Test Project"
    assert project.created_at is not None


@pytest.mark.asyncio
async def test_project_with_components(db_session):
    """Test creating a project with components"""
    project = Project(
        name="Test Project",
        build_server="build-server.local",
    )

    component = Component(
        project=project,
        name="Frontend",
        developer="John Doe",
        vcs_type="git",
        vcs_url="https://github.com/test/repo.git",
    )

    db_session.add(project)
    db_session.add(component)
    await db_session.commit()

    assert component.id is not None
    assert component.project_id == project.id


@pytest.mark.asyncio
async def test_deployment_creation(db_session):
    """Test creating a deployment"""
    project = Project(name="Test Project")
    component = Component(
        project=project,
        name="Frontend",
    )

    deployment = Deployment(
        jira_id="JIRA-001",
        project=project,
        component=component,
        environment="QA",
        build_status="success",
        deploy_status="success",
    )

    db_session.add(project)
    db_session.add(component)
    db_session.add(deployment)
    await db_session.commit()

    assert deployment.id is not None
    assert deployment.jira_id == "JIRA-001"
    assert deployment.timestamp is not None


@pytest.mark.asyncio
async def test_library_creation(db_session):
    """Test creating library"""
    library = Library()

    db_session.add(library)
    await db_session.commit()

    assert library.id is not None
    assert "Kannan" in library.developers
    assert "QA" in library.environments


@pytest.mark.asyncio
async def test_app_settings_creation(db_session):
    """Test creating app settings"""
    setting = AppSettings(
        key="theme",
        value="dark",
        description="Application theme",
    )

    db_session.add(setting)
    await db_session.commit()

    assert setting.id is not None
    assert setting.key == "theme"
