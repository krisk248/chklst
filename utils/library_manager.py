"""
Library Manager for managing reusable presets
Handles developers, servers, environments, etc.
"""

import json
import os
from typing import List, Dict, Any


class LibraryManager:
    """Manages reusable library data (developers, servers, environments)"""

    def __init__(self, library_file: str = "library.json"):
        self.library_file = library_file
        self.ensure_library_file()

    def ensure_library_file(self):
        """Create library file with defaults if it doesn't exist"""
        if not os.path.exists(self.library_file):
            default_library = {
                "developers": ["Kannan"],
                "build_servers": ["192.168.1.149"],
                "deploy_servers": [],
                "environments": ["QA", "UAT", "Production"]
            }
            self.save_library(default_library)

    def load_library(self) -> Dict[str, List[str]]:
        """Load library data from JSON file"""
        try:
            with open(self.library_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading library: {e}")
            return {
                "developers": [],
                "build_servers": [],
                "deploy_servers": [],
                "environments": []
            }

    def save_library(self, library_data: Dict[str, List[str]]) -> bool:
        """Save library data to JSON file"""
        try:
            with open(self.library_file, 'w') as f:
                json.dump(library_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving library: {e}")
            return False

    # Developers
    def get_developers(self) -> List[str]:
        """Get list of developers"""
        library = self.load_library()
        return library.get("developers", [])

    def add_developer(self, name: str) -> bool:
        """Add a developer to the library"""
        if not name or not name.strip():
            return False

        library = self.load_library()
        if name not in library["developers"]:
            library["developers"].append(name)
            return self.save_library(library)
        return False

    def remove_developer(self, name: str) -> bool:
        """Remove a developer from the library"""
        library = self.load_library()
        if name in library["developers"]:
            library["developers"].remove(name)
            return self.save_library(library)
        return False

    # Build Servers
    def get_build_servers(self) -> List[str]:
        """Get list of build servers"""
        library = self.load_library()
        return library.get("build_servers", [])

    def add_build_server(self, server: str) -> bool:
        """Add a build server to the library"""
        if not server or not server.strip():
            return False

        library = self.load_library()
        if server not in library["build_servers"]:
            library["build_servers"].append(server)
            return self.save_library(library)
        return False

    def remove_build_server(self, server: str) -> bool:
        """Remove a build server from the library"""
        library = self.load_library()
        if server in library["build_servers"]:
            library["build_servers"].remove(server)
            return self.save_library(library)
        return False

    # Deploy Servers
    def get_deploy_servers(self) -> List[str]:
        """Get list of deploy servers"""
        library = self.load_library()
        return library.get("deploy_servers", [])

    def add_deploy_server(self, server: str) -> bool:
        """Add a deploy server to the library"""
        if not server or not server.strip():
            return False

        library = self.load_library()
        if server not in library["deploy_servers"]:
            library["deploy_servers"].append(server)
            return self.save_library(library)
        return False

    def remove_deploy_server(self, server: str) -> bool:
        """Remove a deploy server from the library"""
        library = self.load_library()
        if server in library["deploy_servers"]:
            library["deploy_servers"].remove(server)
            return self.save_library(library)
        return False

    # Environments
    def get_environments(self) -> List[str]:
        """Get list of environments"""
        library = self.load_library()
        return library.get("environments", [])

    def add_environment(self, env: str) -> bool:
        """Add an environment to the library"""
        if not env or not env.strip():
            return False

        library = self.load_library()
        if env not in library["environments"]:
            library["environments"].append(env)
            return self.save_library(library)
        return False

    def remove_environment(self, env: str) -> bool:
        """Remove an environment from the library"""
        library = self.load_library()
        if env in library["environments"]:
            library["environments"].remove(env)
            return self.save_library(library)
        return False
