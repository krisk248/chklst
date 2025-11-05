"""
New Projects Tab with Dynamic Component Management
Features component table view and library integration
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QGroupBox, QListWidget,
    QMessageBox, QSplitter, QLabel, QScrollArea,
    QTableWidget, QTableWidgetItem, QDialog, QComboBox,
    QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from utils.json_manager import ProjectJSONManager
from utils.library_manager import LibraryManager


class ComponentEditDialog(QDialog):
    """Dialog for adding/editing components"""

    def __init__(self, component_data=None, parent=None):
        super().__init__(parent)
        self.component_data = component_data or {}
        self.library_manager = LibraryManager()
        self.setWindowTitle("Edit Component" if component_data else "Add Component")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        # Form
        form_layout = QFormLayout()

        # Component Name
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.component_data.get('component_name', ''))
        self.name_edit.setPlaceholderText("e.g., ADX Frontend, Mock Services, etc.")
        form_layout.addRow("Component Name:", self.name_edit)

        # Developer (from library)
        self.developer_combo = QComboBox()
        self.developer_combo.setEditable(True)
        developers = self.library_manager.get_developers()
        self.developer_combo.addItems(developers)
        current_dev = self.component_data.get('developer_name', '')
        if current_dev:
            index = self.developer_combo.findText(current_dev)
            if index >= 0:
                self.developer_combo.setCurrentIndex(index)
            else:
                self.developer_combo.setEditText(current_dev)
        form_layout.addRow("Developer:", self.developer_combo)

        # VCS Type
        self.vcs_type_edit = QLineEdit()
        self.vcs_type_edit.setText(self.component_data.get('vcs_type', 'Git'))
        self.vcs_type_edit.setPlaceholderText("Git, SVN, etc.")
        form_layout.addRow("VCS Type:", self.vcs_type_edit)

        # VCS URL
        self.vcs_url_edit = QLineEdit()
        self.vcs_url_edit.setText(self.component_data.get('vcs_url', ''))
        self.vcs_url_edit.setPlaceholderText("https://github.com/...")
        form_layout.addRow("VCS URL:", self.vcs_url_edit)

        # Build Command
        self.build_command_edit = QLineEdit()
        self.build_command_edit.setText(self.component_data.get('build_command', ''))
        self.build_command_edit.setPlaceholderText("npm build, mvn clean install, etc.")
        form_layout.addRow("Build Command:", self.build_command_edit)

        # Component URL (optional)
        self.component_url_edit = QLineEdit()
        self.component_url_edit.setText(self.component_data.get('component_url', ''))
        self.component_url_edit.setPlaceholderText("https://app.example.com (optional)")
        form_layout.addRow("Component URL:", self.component_url_edit)

        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_component_data(self):
        """Get component data from form"""
        data = {
            'enabled': self.component_data.get('enabled', True),
            'component_name': self.name_edit.text().strip(),
            'developer_name': self.developer_combo.currentText().strip(),
            'vcs_type': self.vcs_type_edit.text().strip(),
            'vcs_url': self.vcs_url_edit.text().strip(),
            'build_command': self.build_command_edit.text().strip(),
            'component_url': self.component_url_edit.text().strip()
        }

        # Preserve ID if editing
        if 'id' in self.component_data:
            data['id'] = self.component_data['id']

        return data


class SimpleProjectsTab(QWidget):
    """New projects management tab with dynamic components"""

    projects_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.json_manager = ProjectJSONManager()
        self.library_manager = LibraryManager()
        self.current_project = None
        self.current_project_data = None
        self.init_ui()
        self.refresh_projects()

    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left side - Project list
        self.create_project_list(splitter)

        # Right side - Project form
        self.create_project_form(splitter)

        splitter.setSizes([300, 700])

    def create_project_list(self, parent):
        """Create project list panel"""
        list_widget = QWidget()
        parent.addWidget(list_widget)

        layout = QVBoxLayout(list_widget)

        # Header
        header = QLabel("📁 PROJECTS")
        header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(header)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("+ New Project")
        self.add_button.clicked.connect(self.add_project)
        button_layout.addWidget(self.add_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Project list
        self.projects_list = QListWidget()
        self.projects_list.itemSelectionChanged.connect(self.on_project_selected)
        layout.addWidget(self.projects_list)

        # Delete button
        self.delete_button = QPushButton("🗑️ Delete Project")
        self.delete_button.clicked.connect(self.delete_project)
        self.delete_button.setEnabled(False)
        layout.addWidget(self.delete_button)

    def create_project_form(self, parent):
        """Create project form panel"""
        scroll = QScrollArea()
        parent.addWidget(scroll)

        form_widget = QWidget()
        scroll.setWidget(form_widget)
        scroll.setWidgetResizable(True)

        layout = QVBoxLayout(form_widget)

        # Project Details Group
        project_group = QGroupBox("📋 PROJECT BASICS")
        project_group.setFont(QFont("Arial", 11, QFont.Bold))
        project_layout = QFormLayout(project_group)

        # Project Name
        self.project_name_edit = QLineEdit()
        project_layout.addRow("Project Name:", self.project_name_edit)

        # Environment (dropdown from library)
        env_layout = QHBoxLayout()
        self.environment_combo = QComboBox()
        self.environment_combo.setEditable(True)
        env_layout.addWidget(self.environment_combo)
        refresh_env_btn = QPushButton("🔄")
        refresh_env_btn.setFixedWidth(40)
        refresh_env_btn.setToolTip("Refresh from Library")
        refresh_env_btn.clicked.connect(self.load_library_data)
        env_layout.addWidget(refresh_env_btn)
        project_layout.addRow("Environment:", env_layout)

        # Build Server (dropdown from library)
        build_layout = QHBoxLayout()
        self.build_server_combo = QComboBox()
        self.build_server_combo.setEditable(True)
        build_layout.addWidget(self.build_server_combo)
        refresh_build_btn = QPushButton("🔄")
        refresh_build_btn.setFixedWidth(40)
        refresh_build_btn.setToolTip("Refresh from Library")
        refresh_build_btn.clicked.connect(self.load_library_data)
        build_layout.addWidget(refresh_build_btn)
        project_layout.addRow("Build Server:", build_layout)

        # Deploy Server (dropdown from library)
        deploy_layout = QHBoxLayout()
        self.deploy_server_combo = QComboBox()
        self.deploy_server_combo.setEditable(True)
        deploy_layout.addWidget(self.deploy_server_combo)
        refresh_deploy_btn = QPushButton("🔄")
        refresh_deploy_btn.setFixedWidth(40)
        refresh_deploy_btn.setToolTip("Refresh from Library")
        refresh_deploy_btn.clicked.connect(self.load_library_data)
        deploy_layout.addWidget(refresh_deploy_btn)
        project_layout.addRow("Deploy Server:", deploy_layout)

        # Database Name
        self.db_name_edit = QLineEdit()
        project_layout.addRow("Database Name:", self.db_name_edit)

        # DB Backup Location
        self.db_backup_location_edit = QLineEdit()
        self.db_backup_location_edit.setPlaceholderText("C:\\TTS\\DBBackups\\UAE\\")
        project_layout.addRow("DB Backup Location:", self.db_backup_location_edit)

        # Backup Location
        self.backup_location_edit = QLineEdit()
        self.backup_location_edit.setPlaceholderText("/backup/project_name/db")
        project_layout.addRow("Backup Location:", self.backup_location_edit)

        layout.addWidget(project_group)

        # Components Group
        components_group = QGroupBox("🧩 COMPONENTS")
        components_group.setFont(QFont("Arial", 11, QFont.Bold))
        components_layout = QVBoxLayout(components_group)

        # Add component button
        add_comp_btn = QPushButton("+ Add Component")
        add_comp_btn.clicked.connect(self.add_component)
        components_layout.addWidget(add_comp_btn)

        # Components table
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(5)
        self.components_table.setHorizontalHeaderLabels(["ON/OFF", "Component Name", "VCS URL", "Component URL", "Actions"])

        # Make table more spacious
        self.components_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # VCS URL
        self.components_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Component URL
        self.components_table.setColumnWidth(0, 80)   # ON/OFF column
        self.components_table.setColumnWidth(1, 200)  # Component Name
        self.components_table.setColumnWidth(4, 220)  # Actions column

        self.components_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.components_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.components_table.setMinimumHeight(250)  # Increased minimum height
        self.components_table.verticalHeader().setDefaultSectionSize(50)  # Taller rows

        components_layout.addWidget(self.components_table)

        layout.addWidget(components_group)

        # Save button
        save_button = QPushButton("💾 Save Project")
        save_button.setFont(QFont("Arial", 11, QFont.Bold))
        save_button.clicked.connect(self.save_project)
        layout.addWidget(save_button)

        layout.addStretch()

        # Load library data
        self.load_library_data()

        # Initially disable form
        self.set_form_enabled(False)

    def load_library_data(self):
        """Load data from library into dropdowns"""
        # Load environments
        self.environment_combo.clear()
        environments = self.library_manager.get_environments()
        self.environment_combo.addItems(environments)

        # Load build servers
        self.build_server_combo.clear()
        build_servers = self.library_manager.get_build_servers()
        self.build_server_combo.addItems(build_servers)

        # Load deploy servers
        self.deploy_server_combo.clear()
        deploy_servers = self.library_manager.get_deploy_servers()
        self.deploy_server_combo.addItems(deploy_servers)

    def set_form_enabled(self, enabled):
        """Enable/disable form elements"""
        self.project_name_edit.setEnabled(enabled)
        self.environment_combo.setEnabled(enabled)
        self.build_server_combo.setEnabled(enabled)
        self.deploy_server_combo.setEnabled(enabled)
        self.db_name_edit.setEnabled(enabled)
        self.db_backup_location_edit.setEnabled(enabled)
        self.backup_location_edit.setEnabled(enabled)
        self.components_table.setEnabled(enabled)

    def refresh_projects(self):
        """Refresh project list"""
        self.projects_list.clear()
        projects = self.json_manager.get_all_projects()
        self.projects_list.addItems(sorted(projects))

    def on_project_selected(self):
        """Handle project selection"""
        current_item = self.projects_list.currentItem()
        if not current_item:
            self.current_project = None
            self.current_project_data = None
            self.set_form_enabled(False)
            self.delete_button.setEnabled(False)
            return

        self.current_project = current_item.text()
        self.load_project_data()
        self.set_form_enabled(True)
        self.delete_button.setEnabled(True)

    def load_project_data(self):
        """Load selected project data into form"""
        if not self.current_project:
            return

        self.current_project_data = self.json_manager.load_project(self.current_project)
        if not self.current_project_data:
            return

        # Load project basics
        self.project_name_edit.setText(self.current_project_data.get('project_name', ''))

        # Set environment
        env = self.current_project_data.get('environment', '')
        index = self.environment_combo.findText(env)
        if index >= 0:
            self.environment_combo.setCurrentIndex(index)
        else:
            self.environment_combo.setEditText(env)

        # Set build server
        build_server = self.current_project_data.get('build_server', '')
        index = self.build_server_combo.findText(build_server)
        if index >= 0:
            self.build_server_combo.setCurrentIndex(index)
        else:
            self.build_server_combo.setEditText(build_server)

        # Set deploy server
        deploy_server = self.current_project_data.get('deploy_server', '')
        index = self.deploy_server_combo.findText(deploy_server)
        if index >= 0:
            self.deploy_server_combo.setCurrentIndex(index)
        else:
            self.deploy_server_combo.setEditText(deploy_server)

        self.db_name_edit.setText(self.current_project_data.get('db_name', ''))
        self.db_backup_location_edit.setText(self.current_project_data.get('db_backup_location', ''))
        self.backup_location_edit.setText(self.current_project_data.get('backup_location', ''))

        # Load components
        self.load_components_table()

    def load_components_table(self):
        """Load components into table"""
        self.components_table.setRowCount(0)

        if not self.current_project:
            return

        components = self.json_manager.get_components(self.current_project)

        for component in components:
            row = self.components_table.rowCount()
            self.components_table.insertRow(row)

            # Enabled status
            enabled_text = "✓" if component.get('enabled', False) else "✗"
            enabled_item = QTableWidgetItem(enabled_text)
            enabled_item.setTextAlignment(Qt.AlignCenter)
            self.components_table.setItem(row, 0, enabled_item)

            # Component name
            name_item = QTableWidgetItem(component.get('component_name', ''))
            self.components_table.setItem(row, 1, name_item)

            # VCS URL
            vcs_url_item = QTableWidgetItem(component.get('vcs_url', ''))
            self.components_table.setItem(row, 2, vcs_url_item)

            # Component URL
            component_url_item = QTableWidgetItem(component.get('component_url', ''))
            self.components_table.setItem(row, 3, component_url_item)

            # Actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)

            toggle_btn = QPushButton("ON" if component.get('enabled') else "OFF")
            toggle_btn.setFixedWidth(50)
            toggle_btn.clicked.connect(lambda checked, comp=component: self.toggle_component(comp))
            actions_layout.addWidget(toggle_btn)

            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(60)
            edit_btn.clicked.connect(lambda checked, comp=component: self.edit_component(comp))
            actions_layout.addWidget(edit_btn)

            remove_btn = QPushButton("×")
            remove_btn.setFixedWidth(30)
            remove_btn.clicked.connect(lambda checked, comp=component: self.remove_component(comp))
            actions_layout.addWidget(remove_btn)

            self.components_table.setCellWidget(row, 4, actions_widget)

    def add_project(self):
        """Add a new project"""
        from PyQt5.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")

        if ok and name:
            # Check if exists
            existing = self.json_manager.load_project(name)
            if existing:
                QMessageBox.warning(self, "Duplicate", f"Project '{name}' already exists!")
                return

            # Create new project with new format
            project_data = self.json_manager.create_new_project_structure(name)

            if self.json_manager.save_project(name, project_data):
                self.refresh_projects()
                self.projects_updated.emit()
                QMessageBox.information(self, "Success", f"Project '{name}' created successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to create project!")

    def delete_project(self):
        """Delete selected project"""
        if not self.current_project:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete project '{self.current_project}'?\n\nThis will remove the JSON file permanently!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.json_manager.delete_project(self.current_project):
                QMessageBox.information(self, "Success", f"Project '{self.current_project}' deleted successfully!")
                self.current_project = None
                self.current_project_data = None
                self.refresh_projects()
                self.projects_updated.emit()
                self.set_form_enabled(False)
            else:
                QMessageBox.critical(self, "Error", "Failed to delete project!")

    def save_project(self):
        """Save current project"""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please select a project first!")
            return

        # Get form data
        new_project_name = self.project_name_edit.text().strip()
        if not new_project_name:
            QMessageBox.warning(self, "Invalid Name", "Project name cannot be empty!")
            return

        # Build project data
        project_data = {
            "project_name": new_project_name,
            "build_server": self.build_server_combo.currentText().strip(),
            "deploy_server": self.deploy_server_combo.currentText().strip(),
            "db_name": self.db_name_edit.text().strip(),
            "db_backup_location": self.db_backup_location_edit.text().strip(),
            "environment": self.environment_combo.currentText().strip(),
            "backup_location": self.backup_location_edit.text().strip(),
            "components": self.json_manager.get_components(self.current_project)  # Preserve components
        }

        # Handle rename
        if new_project_name != self.current_project:
            if self.json_manager.load_project(new_project_name):
                QMessageBox.warning(self, "Duplicate", f"Project '{new_project_name}' already exists!")
                return

            # Delete old, save new
            self.json_manager.delete_project(self.current_project)

        # Save project
        if self.json_manager.save_project(new_project_name, project_data):
            QMessageBox.information(self, "Success", "Project saved successfully!")
            self.current_project = new_project_name
            self.refresh_projects()
            self.projects_updated.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to save project!")

    def add_component(self):
        """Add a new component"""
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please select a project first!")
            return

        dialog = ComponentEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            component_data = dialog.get_component_data()

            if not component_data['component_name']:
                QMessageBox.warning(self, "Invalid", "Component name cannot be empty!")
                return

            if self.json_manager.add_component(self.current_project, component_data):
                self.load_components_table()
                QMessageBox.information(self, "Success", "Component added successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to add component!")

    def edit_component(self, component):
        """Edit a component"""
        dialog = ComponentEditDialog(component_data=component, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            updated_data = dialog.get_component_data()

            # Load project and check format
            project_data = self.json_manager.load_project(self.current_project)
            if not project_data:
                QMessageBox.critical(self, "Error", "Project not found!")
                return

            # Handle both old and new formats
            if self.json_manager.is_new_format(project_data):
                # New format - use update_component
                if self.json_manager.update_component(self.current_project, component['id'], updated_data):
                    self.load_components_table()
                    QMessageBox.information(self, "Success", "Component updated successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to update component!")
            else:
                # Old format - direct update
                comp_type = component.get('id', '').replace('legacy_', '')
                if comp_type in project_data['components']:
                    project_data['components'][comp_type] = updated_data
                    if self.json_manager.save_project(self.current_project, project_data):
                        self.load_components_table()
                        QMessageBox.information(self, "Success", "Component updated successfully!")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to save project!")
                else:
                    QMessageBox.critical(self, "Error", "Component not found!")

    def remove_component(self, component):
        """Remove a component"""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Remove component '{component.get('component_name', '')}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.json_manager.remove_component(self.current_project, component['id']):
                self.load_components_table()
                QMessageBox.information(self, "Success", "Component removed successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to remove component!")

    def toggle_component(self, component):
        """Toggle component enabled status"""
        try:
            project_data = self.json_manager.load_project(self.current_project)
            if not project_data:
                QMessageBox.critical(self, "Error", "Project not found!")
                return

            print(f"DEBUG: Toggling component: {component.get('component_name')}")
            print(f"DEBUG: Is new format: {self.json_manager.is_new_format(project_data)}")

            # Check format
            if self.json_manager.is_new_format(project_data):
                # New format - array of components
                for i, comp in enumerate(project_data['components']):
                    if comp.get('id') == component.get('id'):
                        project_data['components'][i]['enabled'] = not comp.get('enabled', False)
                        print(f"DEBUG: Toggled to: {project_data['components'][i]['enabled']}")
                        break
            else:
                # Old format - migrate and save
                print("DEBUG: Migrating old format...")
                project_data = self.json_manager._migrate_to_new_format(project_data)
                print(f"DEBUG: After migration, components count: {len(project_data['components'])}")
                # Find and toggle
                for i, comp in enumerate(project_data['components']):
                    print(f"DEBUG: Checking comp: {comp.get('component_name')}")
                    if comp.get('component_name') == component.get('component_name'):
                        project_data['components'][i]['enabled'] = not comp.get('enabled', False)
                        print(f"DEBUG: Toggled to: {project_data['components'][i]['enabled']}")
                        break

            print("DEBUG: Attempting to save...")
            result = self.json_manager.save_project(self.current_project, project_data)
            print(f"DEBUG: Save result: {result}")

            if result:
                self.load_components_table()
            else:
                QMessageBox.critical(self, "Error", "save_project returned False - check console for errors")
        except Exception as e:
            print(f"DEBUG ERROR: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Exception: {str(e)}")
