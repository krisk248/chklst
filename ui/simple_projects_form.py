"""
Ultra-Simple Projects Tab - Direct form editing with clean JSON structure
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QGroupBox, 
                             QListWidget, QMessageBox, QTextEdit, QSplitter, 
                             QLabel, QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal

from utils.json_manager import ProjectJSONManager

class SimpleProjectsTab(QWidget):
    """Ultra-simple projects management tab with direct form editing"""
    
    projects_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.json_manager = ProjectJSONManager()
        self.current_project = None
        self.current_project_data = None
        self.init_ui()
        self.refresh_projects()
        
    def init_ui(self):
        """Initialize ultra-simple UI with direct editing"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Project list
        self.create_project_list(splitter)
        
        # Right side - Direct editing form
        self.create_project_form(splitter)
        
        splitter.setSizes([300, 600])
        
    def create_project_list(self, parent):
        """Create simple project list"""
        list_widget = QWidget()
        parent.addWidget(list_widget)
        
        layout = QVBoxLayout(list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Project")
        self.add_button.clicked.connect(self.add_project)

        button_layout.addWidget(self.add_button)
        button_layout.addStretch()

        # Note label for manual deletion
        note_label = QLabel("💡 To delete a project, remove its JSON file from the 'projects' folder")
        note_label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 10px;")
        layout.addWidget(note_label)

        layout.addLayout(button_layout)
        
        # Project list
        self.projects_list = QListWidget()
        self.projects_list.itemSelectionChanged.connect(self.on_project_selected)
        layout.addWidget(self.projects_list)
        
    def create_project_form(self, parent):
        """Create ultra-simple direct editing form"""
        scroll = QScrollArea()
        parent.addWidget(scroll)
        
        form_widget = QWidget()
        scroll.setWidget(form_widget)
        scroll.setWidgetResizable(True)
        
        layout = QVBoxLayout(form_widget)
        
        # Project Details Group
        project_group = QGroupBox("Project Details")
        project_layout = QFormLayout(project_group)
        
        # Project fields - direct editing (NO AUTO-SAVE)
        self.project_name_edit = QLineEdit()
        project_layout.addRow("Project Name:", self.project_name_edit)

        self.build_server_edit = QLineEdit()
        project_layout.addRow("Build Server:", self.build_server_edit)
        
        self.deploy_server_edit = QLineEdit()
        project_layout.addRow("Deploy Server:", self.deploy_server_edit)
        
        self.db_name_edit = QLineEdit()
        project_layout.addRow("DB Name:", self.db_name_edit)

        self.environment_edit = QLineEdit()
        self.environment_edit.setPlaceholderText("QA, UAT, PROD, etc.")
        project_layout.addRow("Environment:", self.environment_edit)

        self.backup_location_edit = QLineEdit()
        self.backup_location_edit.setPlaceholderText("/backup/project_name/db")
        project_layout.addRow("Backup Location:", self.backup_location_edit)

        layout.addWidget(project_group)
        
        # Components Groups - Direct editing for each
        self.create_component_group("Frontend", "frontend", layout)
        self.create_component_group("Backend", "backend", layout) 
        self.create_component_group("BackOffice", "backoffice", layout)
        
        # Save button (though it auto-saves)
        save_button = QPushButton("Save All Changes")
        save_button.clicked.connect(self.save_all_changes)
        layout.addWidget(save_button)
        
        # Initially disable form
        self.set_form_enabled(False)
        
    def create_component_group(self, display_name, component_key, parent_layout):
        """Create a component group with direct editing fields"""
        group = QGroupBox(display_name)
        layout = QFormLayout(group)

        # Enable checkbox (NO AUTO-SAVE)
        enabled_check = QCheckBox(f"Enable {display_name}")
        enabled_check.stateChanged.connect(lambda state, key=component_key: self.on_component_enabled_changed(key, state))
        layout.addRow(enabled_check)

        # Component fields (NO AUTO-SAVE)
        name_edit = QLineEdit()
        layout.addRow("Component Name:", name_edit)

        dev_edit = QLineEdit()
        layout.addRow("Developer Name:", dev_edit)

        vcs_type_edit = QLineEdit()
        layout.addRow("VCS Type:", vcs_type_edit)

        vcs_url_edit = QLineEdit()
        layout.addRow("VCS URL:", vcs_url_edit)

        build_cmd_edit = QLineEdit()
        layout.addRow("Build Command:", build_cmd_edit)

        # Component URL field (only for frontend and backoffice)
        component_url_edit = None
        if component_key in ['frontend', 'backoffice']:
            component_url_edit = QLineEdit()
            component_url_edit.setPlaceholderText("https://example.com/...")
            layout.addRow("Component URL:", component_url_edit)

        # Store references for easy access
        setattr(self, f"{component_key}_enabled_check", enabled_check)
        setattr(self, f"{component_key}_name_edit", name_edit)
        setattr(self, f"{component_key}_dev_edit", dev_edit)
        setattr(self, f"{component_key}_vcs_type_edit", vcs_type_edit)
        setattr(self, f"{component_key}_vcs_url_edit", vcs_url_edit)
        setattr(self, f"{component_key}_build_cmd_edit", build_cmd_edit)
        if component_url_edit:
            setattr(self, f"{component_key}_component_url_edit", component_url_edit)

        parent_layout.addWidget(group)
        
    def set_form_enabled(self, enabled):
        """Enable/disable all form elements"""
        # Project fields
        self.project_name_edit.setEnabled(enabled)
        self.build_server_edit.setEnabled(enabled)
        self.deploy_server_edit.setEnabled(enabled)
        self.db_name_edit.setEnabled(enabled)
        self.environment_edit.setEnabled(enabled)
        self.backup_location_edit.setEnabled(enabled)
        
        # Component fields
        for component in ['frontend', 'backend', 'backoffice']:
            getattr(self, f"{component}_enabled_check").setEnabled(enabled)
            self.set_component_fields_enabled(component, enabled)
            
    def set_component_fields_enabled(self, component_key, enabled):
        """Enable/disable component fields based on enabled checkbox"""
        is_component_enabled = enabled and getattr(self, f"{component_key}_enabled_check").isChecked()

        getattr(self, f"{component_key}_name_edit").setEnabled(is_component_enabled)
        getattr(self, f"{component_key}_dev_edit").setEnabled(is_component_enabled)
        getattr(self, f"{component_key}_vcs_type_edit").setEnabled(is_component_enabled)
        getattr(self, f"{component_key}_vcs_url_edit").setEnabled(is_component_enabled)
        getattr(self, f"{component_key}_build_cmd_edit").setEnabled(is_component_enabled)

        # Enable/disable component URL field if it exists (frontend and backoffice only)
        if hasattr(self, f"{component_key}_component_url_edit"):
            getattr(self, f"{component_key}_component_url_edit").setEnabled(is_component_enabled)
        
    def refresh_projects(self):
        """Refresh project list from JSON files"""
        self.projects_list.clear()
        projects = self.json_manager.get_all_projects()
        for project in sorted(projects):
            self.projects_list.addItem(project)
            
    def on_project_selected(self):
        """Handle project selection"""
        current_item = self.projects_list.currentItem()
        if current_item:
            project_name = current_item.text()
            self.load_project(project_name)
            self.set_form_enabled(True)
        else:
            self.set_form_enabled(False)
            
    def load_project(self, project_name):
        """Load project data from JSON"""
        self.current_project = project_name
        self.current_project_data = self.json_manager.load_project(project_name)
        
        if not self.current_project_data:
            self.current_project_data = self.json_manager.create_default_project_structure(project_name)
            self.json_manager.save_project(project_name, self.current_project_data)
            
        # Load project fields
        self.project_name_edit.setText(self.current_project_data.get('project_name', ''))
        self.build_server_edit.setText(self.current_project_data.get('build_server', '192.168.1.149'))
        self.deploy_server_edit.setText(self.current_project_data.get('deploy_server', ''))
        self.db_name_edit.setText(self.current_project_data.get('db_name', ''))
        self.environment_edit.setText(self.current_project_data.get('environment', 'QA'))
        self.backup_location_edit.setText(self.current_project_data.get('backup_location', ''))

        # Load component data
        components = self.current_project_data.get('components', {})
        for component_key in ['frontend', 'backend', 'backoffice']:
            comp_data = components.get(component_key, {})

            # Set checkbox and enable/disable fields
            enabled_check = getattr(self, f"{component_key}_enabled_check")
            enabled_check.setChecked(comp_data.get('enabled', False))

            # Load component fields
            getattr(self, f"{component_key}_name_edit").setText(comp_data.get('component_name', ''))
            getattr(self, f"{component_key}_dev_edit").setText(comp_data.get('developer_name', ''))
            getattr(self, f"{component_key}_vcs_type_edit").setText(comp_data.get('vcs_type', 'Git'))
            getattr(self, f"{component_key}_vcs_url_edit").setText(comp_data.get('vcs_url', ''))
            getattr(self, f"{component_key}_build_cmd_edit").setText(comp_data.get('build_command', ''))

            # Load component URL if field exists (frontend and backoffice only)
            if hasattr(self, f"{component_key}_component_url_edit"):
                getattr(self, f"{component_key}_component_url_edit").setText(comp_data.get('component_url', ''))

            # Enable/disable component fields based on checkbox
            self.set_component_fields_enabled(component_key, True)
            
    def on_component_enabled_changed(self, component_key, state):
        """Handle component enable/disable (NO AUTO-SAVE)"""
        # Just enable/disable the component fields, no saving
        self.set_component_fields_enabled(component_key, True)
        
    def collect_form_data(self):
        """Collect all form data into project structure"""
        if not self.current_project_data:
            return None

        # Get project-level data from form
        form_data = {
            "project_name": self.project_name_edit.text().strip(),
            "build_server": self.build_server_edit.text().strip(),
            "deploy_server": self.deploy_server_edit.text().strip(),
            "db_name": self.db_name_edit.text().strip(),
            "environment": self.environment_edit.text().strip() or "QA",
            "backup_location": self.backup_location_edit.text().strip(),
            "components": {}
        }

        # Get component data from form
        for component_key in ['frontend', 'backend', 'backoffice']:
            enabled_check = getattr(self, f"{component_key}_enabled_check")
            name_edit = getattr(self, f"{component_key}_name_edit")
            dev_edit = getattr(self, f"{component_key}_dev_edit")
            vcs_type_edit = getattr(self, f"{component_key}_vcs_type_edit")
            vcs_url_edit = getattr(self, f"{component_key}_vcs_url_edit")
            build_cmd_edit = getattr(self, f"{component_key}_build_cmd_edit")

            component_data = {
                "enabled": enabled_check.isChecked(),
                "component_name": name_edit.text().strip(),
                "developer_name": dev_edit.text().strip(),
                "vcs_type": vcs_type_edit.text().strip(),
                "vcs_url": vcs_url_edit.text().strip(),
                "build_command": build_cmd_edit.text().strip()
            }

            # Add component URL if field exists (frontend and backoffice only)
            if hasattr(self, f"{component_key}_component_url_edit"):
                component_url_edit = getattr(self, f"{component_key}_component_url_edit")
                component_data["component_url"] = component_url_edit.text().strip()

            form_data["components"][component_key] = component_data

        return form_data
        
    def add_project(self):
        """Add new project"""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, 'Add Project', 'Project name:')
        if ok and name.strip():
            name = name.strip()
            project_data = self.json_manager.create_default_project_structure(name)
            if self.json_manager.save_project(name, project_data):
                self.refresh_projects()
                # Select the new project
                for i in range(self.projects_list.count()):
                    if self.projects_list.item(i).text() == name:
                        self.projects_list.setCurrentRow(i)
                        break
                self.projects_updated.emit()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create project '{name}'")
                
    def save_all_changes(self):
        """Save all changes - handle project renaming if needed"""
        if not self.current_project:
            QMessageBox.warning(self, "Error", "No project selected!")
            return
            
        # Collect all form data
        form_data = self.collect_form_data()
        if not form_data:
            QMessageBox.warning(self, "Error", "Failed to collect form data!")
            return
        
        old_project_name = self.current_project
        new_project_name = form_data['project_name']
        
        if not new_project_name:
            QMessageBox.warning(self, "Error", "Project name cannot be empty!")
            return
        
        try:
            if old_project_name != new_project_name:
                # Project renamed - delete old, save new
                self.json_manager.delete_project(old_project_name)
                success = self.json_manager.save_project(new_project_name, form_data)
                if success:
                    self.current_project = new_project_name
                    self.current_project_data = form_data
                else:
                    # Restore old project if save failed
                    self.json_manager.save_project(old_project_name, self.current_project_data)
                    QMessageBox.warning(self, "Error", f"Failed to rename project to '{new_project_name}'!")
                    return
            else:
                # Same name - just update
                success = self.json_manager.save_project(old_project_name, form_data)
                if success:
                    self.current_project_data = form_data
                else:
                    QMessageBox.warning(self, "Error", "Failed to save changes!")
                    return
            
            # Success - refresh and show confirmation
            self.refresh_projects()
            
            # Select the current project (old or new name)
            for i in range(self.projects_list.count()):
                if self.projects_list.item(i).text() == self.current_project:
                    self.projects_list.setCurrentRow(i)
                    break
            
            QMessageBox.information(self, "Success", "All changes saved successfully!")
            self.projects_updated.emit()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Save failed: {str(e)}")
                
    def get_projects_list(self):
        """Get list of all projects for other components"""
        return self.json_manager.get_all_projects()
        
    def get_project_data(self, project_name):
        """Get complete project data"""
        return self.json_manager.load_project(project_name)