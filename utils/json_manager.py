import json
import os
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
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving project {project_name}: {e}")
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
        return {
            "project_name": project_name,
            "project_url": project_url,
            "build_server": "192.168.1.149",
            "deploy_server": "",
            "db_name": "",
            "backup_taken": False,
            "backup_location": "",
            "environment": "QA",
            "components": {
                "frontend": {
                    "enabled": True,
                    "component_name": f"{project_name} Frontend",
                    "developer_name": "",
                    "vcs_type": "Git",
                    "vcs_url": "",
                    "build_command": ""
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
                    "build_command": ""
                }
            }
        }