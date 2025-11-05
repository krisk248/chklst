"""
Simple Settings Tab - Basic preferences
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                             QPushButton, QGroupBox, QMessageBox, QFileDialog, QHBoxLayout)
from PyQt5.QtCore import Qt
import json
import os
from utils.settings_manager import get_setting, set_setting

class SimpleSettingsTab(QWidget):
    """Simple settings tab"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # User Defaults
        defaults_group = QGroupBox("User Defaults")
        defaults_layout = QFormLayout(defaults_group)
        
        self.deployed_by_input = QLineEdit()
        self.deployed_by_input.setText(get_setting('deployed_by_default', ''))
        self.deployed_by_input.setPlaceholderText("Your name for deployments")
        defaults_layout.addRow("Deployed By:", self.deployed_by_input)
        
        
        layout.addWidget(defaults_group)
        
        # Excel Export Settings
        export_group = QGroupBox("Excel Export Settings")
        export_layout = QFormLayout(export_group)
        
        # Excel export path with browse button
        path_layout = QHBoxLayout()
        self.export_path_input = QLineEdit()
        self.export_path_input.setText(get_setting('excel_export_path', '/home/kannan/projects/active/chklst/reports'))
        self.export_path_input.setPlaceholderText("/home/user/WORK")
        path_layout.addWidget(self.export_path_input)
        
        browse_button = QPushButton("📁 Browse")
        browse_button.clicked.connect(self.browse_export_path)
        path_layout.addWidget(browse_button)
        
        export_layout.addRow("Base Export Path:", path_layout)
        
        layout.addWidget(export_group)
        
        # Save Button
        save_layout = QVBoxLayout()
        save_layout.addStretch()
        self.save_button = QPushButton("💾 Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_button)
        
        layout.addLayout(save_layout)
        layout.addStretch()
        
    def save_settings(self):
        """Save settings to database"""
        try:
            # Save user defaults
            set_setting('deployed_by_default', self.deployed_by_input.text().strip())
            
            # Save Excel export path
            export_path = self.export_path_input.text().strip()
            if export_path:
                # Validate path exists or can be created
                os.makedirs(export_path, exist_ok=True)
                set_setting('excel_export_path', export_path)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{str(e)}")
            
    def browse_export_path(self):
        """Browse for export path"""
        path = QFileDialog.getExistingDirectory(self, "Select Export Directory")
        if path:
            self.export_path_input.setText(path)