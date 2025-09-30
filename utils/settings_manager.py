"""
Simple File-Based Settings Manager
Replaces database settings with JSON file storage
"""

import json
import os
from typing import Any, Optional
from pathlib import Path


class SettingsManager:
    """Simple file-based settings manager"""
    
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
        
    def _load_settings(self) -> dict:
        """Load settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return {}
        return {}
        
    def _save_settings(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
        
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value"""
        self.settings[key] = value
        return self._save_settings()
        
    def delete_setting(self, key: str) -> bool:
        """Delete a setting"""
        if key in self.settings:
            del self.settings[key]
            return self._save_settings()
        return True
        
    def get_all_settings(self) -> dict:
        """Get all settings"""
        return self.settings.copy()


# Global settings instance
_settings_manager = SettingsManager()


def get_setting(key: str, default: Any = None) -> Any:
    """Get a setting value (compatibility function)"""
    return _settings_manager.get_setting(key, default)


def set_setting(key: str, value: Any) -> bool:
    """Set a setting value (compatibility function)"""
    return _settings_manager.set_setting(key, value)