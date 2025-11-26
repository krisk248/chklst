"""Tests for JSON import service"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path

from backend.services.json_import_service import JSONImportService


@pytest.fixture
def temp_projects_dir():
    """Create temporary projects directory for testing"""
    temp_dir = tempfile.mkdtemp(prefix="test_json_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def import_service(temp_projects_dir):
    """Create import service with temporary directory"""
    return JSONImportService(base_path=temp_projects_dir)


@pytest.fixture
def sample_project_json():
    """Sample project JSON data"""
    return {
        "name": "BRHUB",
        "description": "Branch Hub Project",
        "components": [
            {
                "name": "BR-HUB",
                "description": "Main component"
            }
        ]
    }


class TestJSONImportService:
    """Test JSON import functionality"""

    def test_import_projects_empty_directory(self, import_service):
        """Should return empty list for empty directory"""
        projects = import_service.import_projects_from_json()

        assert projects == []

    def test_import_single_project(self, import_service, temp_projects_dir, sample_project_json):
        """Should import single project from JSON"""
        # Create sample JSON file
        json_file = Path(temp_projects_dir) / "BRHUB.json"
        with open(json_file, "w") as f:
            json.dump(sample_project_json, f)

        projects = import_service.import_projects_from_json()

        assert len(projects) == 1
        assert projects[0]["name"] == "BRHUB"
        assert projects[0]["description"] == "Branch Hub Project"

    def test_import_multiple_projects(self, import_service, temp_projects_dir):
        """Should import multiple project JSON files"""
        project_data = [
            {
                "name": "BRHUB",
                "description": "Branch Hub",
                "components": []
            },
            {
                "name": "ADX-SIP",
                "description": "ADX SIP",
                "components": []
            },
            {
                "name": "MBANK",
                "description": "Mobile Bank",
                "components": []
            }
        ]

        # Create JSON files
        for project in project_data:
            json_file = Path(temp_projects_dir) / f"{project['name']}.json"
            with open(json_file, "w") as f:
                json.dump(project, f)

        projects = import_service.import_projects_from_json()

        assert len(projects) == 3
        project_names = [p["name"] for p in projects]
        assert "BRHUB" in project_names
        assert "ADX-SIP" in project_names
        assert "MBANK" in project_names

    def test_import_project_with_components(self, import_service, temp_projects_dir):
        """Should import project with components"""
        project_data = {
            "name": "BRHUB",
            "description": "Branch Hub",
            "components": [
                {
                    "name": "BR-HUB",
                    "description": "Main component"
                },
                {
                    "name": "BR-API",
                    "description": "API component"
                }
            ]
        }

        json_file = Path(temp_projects_dir) / "BRHUB.json"
        with open(json_file, "w") as f:
            json.dump(project_data, f)

        projects = import_service.import_projects_from_json()

        assert len(projects) == 1
        assert len(projects[0]["components"]) == 2
        assert projects[0]["components"][0]["name"] == "BR-HUB"
        assert projects[0]["components"][1]["name"] == "BR-API"

    def test_import_handles_invalid_json(self, import_service, temp_projects_dir):
        """Should skip invalid JSON files gracefully"""
        # Create valid JSON
        valid_file = Path(temp_projects_dir) / "valid.json"
        with open(valid_file, "w") as f:
            json.dump({"name": "VALID"}, f)

        # Create invalid JSON
        invalid_file = Path(temp_projects_dir) / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{ invalid json }")

        projects = import_service.import_projects_from_json()

        # Should only import valid file
        assert len(projects) == 1
        assert projects[0]["name"] == "VALID"

    def test_import_returns_sorted_by_name(self, import_service, temp_projects_dir):
        """Should return projects sorted by name"""
        project_names = ["ZEBRA", "ALPHA", "BETA"]

        for name in project_names:
            json_file = Path(temp_projects_dir) / f"{name}.json"
            with open(json_file, "w") as f:
                json.dump({"name": name}, f)

        projects = import_service.import_projects_from_json()

        returned_names = [p["name"] for p in projects]
        assert returned_names == ["ALPHA", "BETA", "ZEBRA"]

    def test_get_project_summary(self, import_service, temp_projects_dir):
        """Should return summary of imported projects"""
        # Create multiple projects
        for i, name in enumerate(["BRHUB", "ADX-SIP", "MBANK"]):
            project_data = {
                "name": name,
                "description": f"Project {i+1}",
                "components": [{"name": f"Component-{j}"} for j in range(2)]
            }
            json_file = Path(temp_projects_dir) / f"{name}.json"
            with open(json_file, "w") as f:
                json.dump(project_data, f)

        summary = import_service.get_import_summary()

        assert summary["total_projects"] == 3
        assert summary["total_components"] == 6
        assert summary["projects_list"] == ["ADX-SIP", "BRHUB", "MBANK"]
