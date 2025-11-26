"""JSON import service for importing projects and components from JSON files"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class JSONImportService:
    """Service for importing project data from JSON files"""

    def __init__(self, base_path: str = "projects"):
        """Initialize JSON import service with projects directory"""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def import_projects_from_json(self) -> List[Dict[str, Any]]:
        """Read all project JSON files and return data"""
        projects = []

        if not self.base_path.exists():
            return projects

        for json_file in sorted(self.base_path.glob("*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    project_data = json.load(f)
                    projects.append(project_data)
            except (json.JSONDecodeError, IOError) as e:
                # Skip invalid JSON files
                continue

        # Sort by name for consistent ordering
        projects.sort(key=lambda p: p.get("name", "").lower())
        return projects

    def get_import_summary(self) -> Dict[str, Any]:
        """Get summary of imported projects"""
        projects = self.import_projects_from_json()

        total_components = 0
        for project in projects:
            components = project.get("components", [])
            total_components += len(components)

        return {
            "total_projects": len(projects),
            "total_components": total_components,
            "projects_list": sorted([p.get("name", "") for p in projects])
        }

    def get_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get specific project by name"""
        projects = self.import_projects_from_json()

        for project in projects:
            if project.get("name") == project_name:
                return project

        return None

    def get_project_components(self, project_name: str) -> List[Dict[str, Any]]:
        """Get components for a specific project"""
        project = self.get_project(project_name)

        if project:
            return project.get("components", [])

        return []
