"""Tests for Excel export API endpoint"""

import pytest
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

from fastapi.testclient import TestClient
from backend.main import app
from backend.services.excel_service import ExcelService


@pytest.fixture
def temp_reports_dir(monkeypatch):
    """Create temporary reports directory and patch ExcelService"""
    temp_dir = tempfile.mkdtemp(prefix="test_excel_export_")

    # Patch the ExcelService base_path
    def patched_init(self, base_path="reports"):
        self.base_path = Path(temp_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(ExcelService, "__init__", patched_init)

    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def excel_service():
    """Create Excel service instance"""
    return ExcelService()


class TestExcelExportEndpoint:
    """Test Excel export API endpoint"""

    def test_export_excel_no_data(self, client, temp_reports_dir):
        """Should return 200 with Excel file when no data exists"""
        response = client.get("/api/v1/reports/excel?month=11&year=2025")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def test_export_excel_with_data(self, client, temp_reports_dir, excel_service):
        """Should return Excel file with deployment data"""
        # Create sample data
        deployment_data = {
            "jira_id": "PAT-001",
            "project_name": "BRHUB",
            "timestamp": datetime(2025, 11, 26, 10, 30),
            "component_name": "BR-HUB",
            "environment": "QA",
            "vcs_url": "https://github.com/example/repo",
            "developer_name": "John Doe",
            "build_server": "192.168.1.149",
            "deploy_server": "192.168.1.60",
            "db_name": "BR_HUB_QA",
            "db_backup_location": "/backup/path",
            "db_script": "script.sql",
            "build_backup": "/backup/build",
            "build_status": True,
            "deploy_status": True,
            "notes": "Test deployment",
            "deployed_by": "Kannan"
        }
        excel_service.save_deployment(deployment_data)

        response = client.get("/api/v1/reports/excel?month=11&year=2025")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert len(response.content) > 0

    def test_export_excel_invalid_month(self, client, temp_reports_dir):
        """Should reject invalid month parameter"""
        response = client.get("/api/v1/reports/excel?month=13&year=2025")

        assert response.status_code == 400  # Bad request

    def test_export_excel_invalid_year(self, client, temp_reports_dir):
        """Should reject invalid year parameter"""
        response = client.get("/api/v1/reports/excel?month=11&year=1900")

        assert response.status_code == 400  # Bad request

    def test_export_excel_missing_parameters(self, client, temp_reports_dir):
        """Should reject request without required parameters"""
        response = client.get("/api/v1/reports/excel")

        assert response.status_code == 422  # Missing parameters

    def test_export_excel_content_disposition(self, client, temp_reports_dir, excel_service):
        """Should set correct Content-Disposition header"""
        deployment_data = {
            "jira_id": "PAT-001",
            "project_name": "BRHUB",
            "timestamp": datetime(2025, 11, 26, 10, 30),
            "component_name": "BR-HUB",
            "environment": "QA",
            "vcs_url": "https://github.com/example/repo",
            "developer_name": "John Doe",
            "build_server": "192.168.1.149",
            "deploy_server": "192.168.1.60",
            "db_name": "BR_HUB_QA",
            "db_backup_location": "/backup/path",
            "db_script": "script.sql",
            "build_backup": "/backup/build",
            "build_status": True,
            "deploy_status": True,
            "notes": "Test deployment",
            "deployed_by": "Kannan"
        }
        excel_service.save_deployment(deployment_data)

        response = client.get("/api/v1/reports/excel?month=11&year=2025")

        assert response.status_code == 200
        assert "content-disposition" in response.headers or "Content-Disposition" in response.headers

    def test_export_excel_multiple_projects(self, client, temp_reports_dir, excel_service):
        """Should return combined Excel for multiple projects"""
        projects = ["BRHUB", "ADX-SIP"]
        for i, project in enumerate(projects):
            deployment_data = {
                "jira_id": f"PAT-{i+1:03d}",
                "project_name": project,
                "timestamp": datetime(2025, 11, 26, 10, 30),
                "component_name": f"Component-{i+1}",
                "environment": "QA",
                "vcs_url": "https://github.com/example/repo",
                "developer_name": "John Doe",
                "build_server": "192.168.1.149",
                "deploy_server": "192.168.1.60",
                "db_name": "DB_NAME",
                "db_backup_location": "/backup/path",
                "db_script": "script.sql",
                "build_backup": "/backup/build",
                "build_status": True,
                "deploy_status": True,
                "notes": f"Deployment for {project}",
                "deployed_by": "Kannan"
            }
            excel_service.save_deployment(deployment_data)

        response = client.get("/api/v1/reports/excel?month=11&year=2025")

        assert response.status_code == 200
        assert len(response.content) > 0
