import json
import os
import uuid
from typing import Dict, List, Any, Optional

class ProjectJSONManager:
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = projects_dir
        self.ensure_projects_dir()
    
    def ensure_projects_dir(self):
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
    
    def get_project_file_path(self, project_name: str) -> str:
        safe_name = project_name.replace(" ", "_").replace("/", "_")
        return os.path.join(self.projects_dir, f"{safe_name}.json")
    
    def save_project(self, project_name: str, project_data: Dict[str, Any]) -> bool:
        try:
            file_path = self.get_project_file_path(project_name)
            print(f"DEBUG save_project: Saving to {file_path}")
            print(f"DEBUG save_project: Data keys: {list(project_data.keys())}")
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=2)
            print(f"DEBUG save_project: Successfully saved")
            return True
        except Exception as e:
            print(f"ERROR save_project {project_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        try:
            file_path = self.get_project_file_path(project_name)
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project {project_name}: {e}")
            return None
    
    def get_all_projects(self) -> List[str]:
        try:
            if not os.path.exists(self.projects_dir):
                return []
            files = [f for f in os.listdir(self.projects_dir) if f.endswith('.json')]
            return [f.replace('.json', '').replace('_', ' ') for f in files]
        except Exception as e:
            print(f"Error getting all projects: {e}")
            return []
    
    def delete_project(self, project_name: str) -> bool:
        try:
            file_path = self.get_project_file_path(project_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting project {project_name}: {e}")
            return False
    
    def rename_project(self, old_name: str, new_name: str) -> bool:
        try:
            old_data = self.load_project(old_name)
            if old_data is None:
                return False
            
            old_data['project_name'] = new_name
            if self.save_project(new_name, old_data):
                self.delete_project(old_name)
                return True
            return False
        except Exception as e:
            print(f"Error renaming project {old_name} to {new_name}: {e}")
            return False

    def create_default_project_structure(self, project_name: str, project_url: str = "") -> Dict[str, Any]:
        """Create default project structure (OLD FORMAT - for backward compatibility)"""
        return {
            "project_name": project_name,
            "build_server": "192.168.1.149",
            "deploy_server": "",
            "db_name": "",
            "db_backup_location": "",
            "environment": "QA",
            "backup_location": "",
            "components": {
                "frontend": {
                    "enabled": True,
                    "component_name": f"{project_name} Frontend",
                    "developer_name": "",
                    "vcs_type": "Git",
                    "vcs_url": "",
                    "build_command": "",
                    "component_url": ""
                },
                "backend": {
                    "enabled": True,
                    "component_name": f"{project_name} Backend",
                    "developer_name": "",
                    "vcs_type": "Git",
                    "vcs_url": "",
                    "build_command": ""
                },
                "backoffice": {
                    "enabled": False,
                    "component_name": "",
                    "developer_name": "",
                    "vcs_type": "",
                    "vcs_url": "",
                    "build_command": "",
                    "component_url": ""
                }
            }
        }

    # New methods for dynamic components (v2 format)
    def create_new_project_structure(self, project_name: str) -> Dict[str, Any]:
        """Create new project structure with dynamic components (NEW FORMAT)"""
        return {
            "project_name": project_name,
            "build_server": "",
            "deploy_server": "",
            "db_name": "",
            "db_backup_location": "",
            "environment": "QA",
            "backup_location": "",
            "components": []  # Empty list of components
        }

    def is_new_format(self, project_data: Dict[str, Any]) -> bool:
        """Check if project uses new format (list of components)"""
        if not project_data or 'components' not in project_data:
            return False
        return isinstance(project_data['components'], list)

    def get_components(self, project_name: str) -> List[Dict[str, Any]]:
        """Get all components for a project (works with both formats)"""
        project_data = self.load_project(project_name)
        if not project_data:
            return []

        if self.is_new_format(project_data):
            return project_data.get('components', [])
        else:
            # Convert old format to list format on-the-fly
            components = []
            old_components = project_data.get('components', {})
            for comp_type, comp_data in old_components.items():
                if comp_data.get('enabled', False):
                    components.append({
                        'id': f'legacy_{comp_type}',
                        'enabled': comp_data.get('enabled', False),
                        'component_name': comp_data.get('component_name', ''),
                        'developer_name': comp_data.get('developer_name', ''),
                        'vcs_type': comp_data.get('vcs_type', ''),
                        'vcs_url': comp_data.get('vcs_url', ''),
                        'build_command': comp_data.get('build_command', ''),
                        'component_url': comp_data.get('component_url', '')
                    })
            return components

    def get_enabled_components(self, project_name: str) -> List[Dict[str, Any]]:
        """Get only enabled components for a project"""
        components = self.get_components(project_name)
        return [comp for comp in components if comp.get('enabled', False)]

    def add_component(self, project_name: str, component_data: Dict[str, Any]) -> bool:
        """Add a new component to a project"""
        try:
            project_data = self.load_project(project_name)
            if not project_data:
                return False

            # Ensure new format
            if not self.is_new_format(project_data):
                project_data = self._migrate_to_new_format(project_data)

            # Generate ID if not provided
            if 'id' not in component_data:
                component_data['id'] = str(uuid.uuid4())[:8]

            # Add component to list
            project_data['components'].append(component_data)

            return self.save_project(project_name, project_data)
        except Exception as e:
            print(f"Error adding component to {project_name}: {e}")
            return False

    def update_component(self, project_name: str, component_id: str, component_data: Dict[str, Any]) -> bool:
        """Update an existing component"""
        try:
            project_data = self.load_project(project_name)
            if not project_data or not self.is_new_format(project_data):
                return False

            # Find and update component
            for i, comp in enumerate(project_data['components']):
                if comp.get('id') == component_id:
                    component_data['id'] = component_id  # Preserve ID
                    project_data['components'][i] = component_data
                    return self.save_project(project_name, project_data)

            return False
        except Exception as e:
            print(f"Error updating component in {project_name}: {e}")
            return False

    def remove_component(self, project_name: str, component_id: str) -> bool:
        """Remove a component from a project"""
        try:
            project_data = self.load_project(project_name)
            if not project_data or not self.is_new_format(project_data):
                return False

            # Remove component with matching ID
            project_data['components'] = [
                comp for comp in project_data['components']
                if comp.get('id') != component_id
            ]

            return self.save_project(project_name, project_data)
        except Exception as e:
            print(f"Error removing component from {project_name}: {e}")
            return False

    def _migrate_to_new_format(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old format project to new format"""
        if self.is_new_format(project_data):
            return project_data

        new_project = {
            "project_name": project_data.get("project_name", ""),
            "build_server": project_data.get("build_server", ""),
            "deploy_server": project_data.get("deploy_server", ""),
            "db_name": project_data.get("db_name", ""),
            "db_backup_location": project_data.get("db_backup_location", ""),
            "environment": project_data.get("environment", "QA"),
            "backup_location": project_data.get("backup_location", ""),
            "components": []
        }

        # Convert old components
        old_components = project_data.get('components', {})
        for comp_type, comp_data in old_components.items():
            component = {
                'id': f'migrated_{comp_type}_{uuid.uuid4().hex[:6]}',
                'enabled': comp_data.get('enabled', False),
                'component_name': comp_data.get('component_name', ''),
                'vcs_type': comp_data.get('vcs_type', 'Git'),
                'vcs_url': comp_data.get('vcs_url', ''),
                'build_command': comp_data.get('build_command', ''),
                'component_url': comp_data.get('component_url', '')
            }
            new_project['components'].append(component)

        return new_project

    def migrate_project_to_new_format(self, project_name: str) -> bool:
        """Explicitly migrate a project from old to new format"""
        try:
            project_data = self.load_project(project_name)
            if not project_data:
                return False

            if self.is_new_format(project_data):
                return True  # Already in new format

            new_project = self._migrate_to_new_format(project_data)
            return self.save_project(project_name, new_project)
        except Exception as e:
            print(f"Error migrating project {project_name}: {e}")
            return False