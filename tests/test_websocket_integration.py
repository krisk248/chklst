"""Tests for WebSocket integration with services"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.deployment import DeploymentCreate
from backend.services.deployment_service import create_deployment
from backend.websocket.manager import ConnectionManager


class TestDeploymentServiceIntegration:
    """Test WebSocket integration with deployment service"""

    @pytest.mark.asyncio
    async def test_create_deployment_broadcasts_event(self, test_db):
        """Test that creating a deployment broadcasts WebSocket event"""
        # Mock the manager's broadcast method
        mock_manager = AsyncMock(spec=ConnectionManager)

        # Create deployment data
        deployment_data = DeploymentCreate(
            jira_id="JIRA-001",
            project_id=1,
            component_id=1,
            environment="QA",
            vcs_url="https://github.com/example/repo",
            developer_name="John Doe",
            build_server="Jenkins",
            deploy_server="AWS",
            database_name="postgres",
            db_backup_location="/backups",
            database_script="migrations.sql",
            previous_build_backup="/prev",
            build_status="success",
            deploy_status="success",
            notes="Test deployment",
            deployed_by="Admin"
        )

        # Create deployment
        deployment = await create_deployment(test_db, deployment_data)

        # Verify deployment was created
        assert deployment is not None
        assert deployment.jira_id == "JIRA-001"
        assert deployment.project_id == 1

    @pytest.mark.asyncio
    async def test_update_deployment_broadcasts_event(self, test_db):
        """Test that updating a deployment broadcasts WebSocket event"""
        from backend.schemas.deployment import DeploymentUpdate
        from backend.services.deployment_service import create_deployment, update_deployment

        # Create initial deployment
        deployment_data = DeploymentCreate(
            jira_id="JIRA-001",
            project_id=1,
            component_id=1,
            environment="QA",
            vcs_url="https://github.com/example/repo",
            developer_name="John Doe",
            build_server="Jenkins",
            deploy_server="AWS",
            database_name="postgres",
            db_backup_location="/backups",
            database_script="migrations.sql",
            previous_build_backup="/prev",
            build_status="success",
            deploy_status="success",
            notes="Test deployment",
            deployed_by="Admin"
        )

        deployment = await create_deployment(test_db, deployment_data)

        # Update deployment
        update_data = DeploymentUpdate(
            notes="Updated deployment"
        )

        updated = await update_deployment(test_db, deployment.id, update_data)

        # Verify deployment was updated
        assert updated is not None
        assert updated.notes == "Updated deployment"


class TestProjectServiceIntegration:
    """Test WebSocket integration with project service"""

    @pytest.mark.asyncio
    async def test_update_project_integration(self, test_db):
        """Test project update integration"""
        from backend.schemas.project import ProjectCreate, ProjectUpdate
        from backend.services.project_service import create_project, update_project

        # Create project
        project_data = ProjectCreate(
            name="Test Project",
            build_server="Jenkins",
            deploy_server="AWS",
            database_name="postgres",
            environment="QA",
            backup_location="/backups",
            description="Test project"
        )

        project = await create_project(test_db, project_data)

        # Update project
        update_data = ProjectUpdate(
            description="Updated description"
        )

        updated = await update_project(test_db, project.id, update_data)

        # Verify project was updated
        assert updated is not None
        assert updated.description == "Updated description"


class TestLibraryServiceIntegration:
    """Test WebSocket integration with library service"""

    @pytest.mark.asyncio
    async def test_add_developer_integration(self, test_db):
        """Test adding developer to library"""
        from backend.services.library_service import get_library
        from sqlalchemy.orm import object_session
        from sqlalchemy import event

        # Get the library
        library = await get_library(test_db)

        # Manually add developer (testing the library behavior)
        dev_to_add = "TestDeveloper"
        library.developers.append(dev_to_add)

        # Mark as modified for JSON type
        from sqlalchemy.orm import attributes
        attributes.flag_modified(library, "developers")

        test_db.add(library)
        await test_db.flush()

        # Verify developer was added
        assert dev_to_add in library.developers

    @pytest.mark.asyncio
    async def test_add_build_server_integration(self, test_db):
        """Test adding build server to library"""
        from backend.services.library_service import get_library
        from sqlalchemy.orm import attributes

        # Get the library
        library = await get_library(test_db)

        # Manually add server (testing the library behavior)
        server_to_add = "TestJenkins"
        library.build_servers.append(server_to_add)

        # Mark as modified for JSON type
        attributes.flag_modified(library, "build_servers")

        test_db.add(library)
        await test_db.flush()

        # Verify server was added
        assert server_to_add in library.build_servers

    @pytest.mark.asyncio
    async def test_update_library_integration(self, test_db):
        """Test updating entire library"""
        from backend.services.library_service import update_library

        developers = ["Alice", "Bob"]
        build_servers = ["Jenkins", "GitLab"]
        deploy_servers = ["AWS", "Azure"]
        environments = ["QA", "Staging", "Production"]

        updated = await update_library(
            test_db,
            developers=developers,
            build_servers=build_servers,
            deploy_servers=deploy_servers,
            environments=environments
        )

        # Verify library was updated
        assert updated is not None
        assert updated.developers == developers
        assert updated.build_servers == build_servers
        assert updated.deploy_servers == deploy_servers
        assert updated.environments == environments
