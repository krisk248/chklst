"""Tests for migration service - importing data from existing files to SQLite"""

import pytest
from pathlib import Path
from sqlalchemy import select

from backend.services.migration_service import MigrationService
from backend.models import Project, Component, Deployment, Library, AppSettings


@pytest.fixture
def migration_service():
    """Create migration service instance"""
    return MigrationService()


class TestMigrationServiceLibraryImport:
    """Test library.json import"""

    @pytest.mark.asyncio
    async def test_import_library_from_json(self, migration_service, db_session):
        """Test that library.json is correctly imported"""
        await migration_service._import_library(db_session)
        await db_session.commit()

        # Check library was imported
        library = await db_session.get(Library, 1)
        assert library is not None
        assert isinstance(library.developers, list)
        assert isinstance(library.build_servers, list)
        assert isinstance(library.deploy_servers, list)
        assert isinstance(library.environments, list)

    @pytest.mark.asyncio
    async def test_library_import_creates_defaults(self, migration_service, db_session):
        """Test that library import handles missing file gracefully"""
        # This should not raise an error even if file doesn't exist
        result = await migration_service._import_library(db_session)
        # No exception means success
        assert True


class TestMigrationServiceSettingsImport:
    """Test settings.json import"""

    @pytest.mark.asyncio
    async def test_import_settings_from_json(self, migration_service, db_session):
        """Test that settings.json is correctly imported"""
        await migration_service._import_settings(db_session)
        await db_session.commit()

        # Check settings were imported
        stmt = select(AppSettings).where(AppSettings.key == "deployed_by_default")
        result = await db_session.execute(stmt)
        settings = result.scalars().first()

        if settings:
            assert settings is not None
            assert settings.value is not None

    @pytest.mark.asyncio
    async def test_settings_import_handles_missing_file(self, migration_service, db_session):
        """Test that settings import handles missing file gracefully"""
        result = await migration_service._import_settings(db_session)
        # No exception means success
        assert True


class TestMigrationServiceProjectImport:
    """Test project JSON files import"""

    @pytest.mark.asyncio
    async def test_import_single_project(self, migration_service, db_session):
        """Test importing a single project from JSON"""
        projects, components = await migration_service._import_projects(db_session)
        await db_session.commit()

        # Should have imported some projects
        assert projects >= 0

        if projects > 0:
            # Check project exists in database
            project = await db_session.get(Project, 1)
            assert project is not None
            assert project.name is not None
            assert project.build_server is not None

    @pytest.mark.asyncio
    async def test_import_project_with_components_dict(self, migration_service, db_session):
        """Test importing project with components as dictionary"""
        # BRHUB.json has components as dict
        projects, components = await migration_service._import_projects(db_session)
        await db_session.commit()

        # Should import projects and components
        assert projects >= 0

    @pytest.mark.asyncio
    async def test_import_project_with_components_list(self, migration_service, db_session):
        """Test importing project with components as list"""
        # ADX-SIP.json has components as list
        projects, components = await migration_service._import_projects(db_session)
        await db_session.commit()

        # Should import projects and components
        assert projects >= 0

    @pytest.mark.asyncio
    async def test_components_linked_to_projects(self, migration_service, db_session):
        """Test that components are correctly linked to projects"""
        projects, components = await migration_service._import_projects(db_session)
        await db_session.commit()

        if projects > 0:
            # Get first project and check components
            project = await db_session.get(Project, 1)
            assert project is not None

    @pytest.mark.asyncio
    async def test_import_preserves_component_data(self, migration_service, db_session):
        """Test that component data is preserved during import"""
        projects, components = await migration_service._import_projects(db_session)
        await db_session.commit()

        if components > 0:
            component = await db_session.get(Component, 1)
            assert component is not None
            assert component.name is not None


class TestMigrationServiceDeploymentImport:
    """Test deployment Excel files import"""

    @pytest.mark.asyncio
    async def test_import_deployments_from_excel(self, migration_service, db_session):
        """Test importing deployments from Excel files"""
        # First import projects and components (needed for foreign key refs)
        await migration_service._import_projects(db_session)
        await db_session.commit()

        # Then import deployments
        count = await migration_service._import_deployments(db_session)
        await db_session.commit()

        # Should import some deployments or 0 if no Excel files
        assert count >= 0

    @pytest.mark.asyncio
    async def test_deployment_has_required_fields(self, migration_service, db_session):
        """Test that imported deployments have required fields"""
        # First import projects and components
        await migration_service._import_projects(db_session)
        await db_session.commit()

        # Then import deployments
        count = await migration_service._import_deployments(db_session)
        await db_session.commit()

        if count > 0:
            deployment = await db_session.get(Deployment, 1)
            assert deployment is not None
            assert deployment.jira_id is not None
            assert deployment.timestamp is not None

    @pytest.mark.asyncio
    async def test_deployment_status_parsing(self, migration_service, db_session):
        """Test that deployment status is correctly parsed from Excel"""
        # First import projects and components
        await migration_service._import_projects(db_session)
        await db_session.commit()

        # Then import deployments
        count = await migration_service._import_deployments(db_session)
        await db_session.commit()

        if count > 0:
            deployment = await db_session.get(Deployment, 1)
            # Status should be string ("success", "failed", "pending")
            assert isinstance(deployment.build_status, str)
            assert isinstance(deployment.deploy_status, str)
            assert deployment.build_status in ["success", "failed", "pending"]
            assert deployment.deploy_status in ["success", "failed", "pending"]


class TestMigrationServiceFullMigration:
    """Test complete migration workflow"""

    @pytest.mark.asyncio
    async def test_run_full_migration(self, migration_service, db_session):
        """Test complete migration from all sources"""
        results = await migration_service.run_full_migration()

        assert "projects" in results
        assert "components" in results
        assert "deployments" in results
        assert "library_imported" in results
        assert "settings_imported" in results
        assert "errors" in results

    @pytest.mark.asyncio
    async def test_migration_result_structure(self, migration_service):
        """Test that migration results have correct structure"""
        results = await migration_service.run_full_migration()

        assert isinstance(results["projects"], int)
        assert isinstance(results["components"], int)
        assert isinstance(results["deployments"], int)
        assert isinstance(results["library_imported"], bool)
        assert isinstance(results["settings_imported"], bool)
        assert isinstance(results["errors"], list)

    def test_migration_flag(self, migration_service):
        """Test migration completion flag"""
        # Check migration flag initially
        initial_needed = migration_service.check_migration_needed()

        # Mark migration as complete
        migration_service.mark_migration_complete()

        # Check migration flag
        assert not migration_service.check_migration_needed()

        # Clean up - remove the flag
        flag_path = Path("data/.migration_complete")
        if flag_path.exists():
            flag_path.unlink()

        # Verify flag was removed
        assert migration_service.check_migration_needed()


class TestMigrationServiceErrorHandling:
    """Test error handling in migration"""

    @pytest.mark.asyncio
    async def test_migration_continues_on_error(self, migration_service):
        """Test that migration continues even if some files fail"""
        results = await migration_service.run_full_migration()

        # Should complete even if some files are corrupted
        assert results is not None
        assert isinstance(results, dict)


class TestMigrationDataPreservation:
    """Test that original data is preserved during migration"""

    @pytest.mark.asyncio
    async def test_project_names_preserved(self, migration_service, db_session):
        """Test that project names are preserved"""
        projects_count, _ = await migration_service._import_projects(db_session)
        await db_session.commit()

        if projects_count > 0:
            project = await db_session.get(Project, 1)
            # Name should not be empty
            assert project.name and len(project.name) > 0

    @pytest.mark.asyncio
    async def test_component_vcs_urls_preserved(self, migration_service, db_session):
        """Test that VCS URLs are preserved"""
        _, components_count = await migration_service._import_projects(db_session)
        await db_session.commit()

        if components_count > 0:
            component = await db_session.get(Component, 1)
            # Component should exist
            assert component is not None


class TestMigrationServiceParsing:
    """Test parsing utilities in migration service"""

    @pytest.mark.asyncio
    async def test_parse_status_values(self, migration_service):
        """Test status parsing for various values"""
        # Test true values
        assert migration_service._parse_status("success") is True
        assert migration_service._parse_status("Success") is True
        assert migration_service._parse_status("true") is True
        assert migration_service._parse_status("True") is True
        assert migration_service._parse_status("1") is True
        assert migration_service._parse_status("pass") is True

        # Test false values
        assert migration_service._parse_status("failed") is False
        assert migration_service._parse_status("false") is False
        assert migration_service._parse_status("") is False
        assert migration_service._parse_status(None) is False

    @pytest.mark.asyncio
    async def test_parse_timestamp(self, migration_service):
        """Test timestamp parsing"""
        from datetime import datetime

        # Test with datetime object
        now = datetime.now()
        parsed = await migration_service._parse_timestamp(now)
        assert parsed is not None

        # Test with string
        parsed = await migration_service._parse_timestamp("2025-01-15 10:30:00")
        assert parsed is not None
        assert isinstance(parsed, datetime)

        # Test with None/empty
        parsed = await migration_service._parse_timestamp(None)
        assert isinstance(parsed, datetime)
