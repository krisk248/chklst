"""
NEW Streamlined Deployment Form with Dropdowns
Ultra-simple daily workflow with library integration
"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QComboBox, QLineEdit, QTextEdit, QCheckBox, QPushButton,
    QGroupBox, QDateTimeEdit, QMessageBox, QScrollArea,
    QRadioButton, QApplication
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QFont

from utils.json_manager import ProjectJSONManager
from utils.excel_manager import ExcelManager
from utils.integration_formatter import JiraFormatter, TeamsFormatter
from utils.settings_manager import get_setting
from utils.library_manager import LibraryManager


class SimpleDeploymentForm(QWidget):
    """NEW streamlined deployment form with dropdowns"""

    def __init__(self):
        super().__init__()
        self.json_manager = ProjectJSONManager()
        self.excel_manager = ExcelManager()
        self.library_manager = LibraryManager()

        self.current_project_data = None
        self.current_component_data = None
        self.last_saved_data = None  # For copy buttons

        self.init_ui()
        self.load_projects()

    def init_ui(self):
        """Initialize UI"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("📝 NEW DEPLOYMENT")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #4a9eff; margin: 10px;")
        layout.addWidget(title)

        # Project & Component Selection
        self.setup_project_selection(layout)

        # Auto-filled Section
        self.setup_auto_filled_section(layout)

        # User Input Section
        self.setup_user_input_section(layout)

        # Buttons Section (All in one place)
        self.setup_buttons_section(layout)

        layout.addStretch()
        main_widget.setLayout(layout)
        scroll.setWidget(main_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def setup_project_selection(self, layout):
        """Setup project and component selection with dropdowns"""
        group = QGroupBox("🎯 PROJECT & COMPONENT")
        group.setFont(QFont("Arial", 11, QFont.Bold))

        form_layout = QFormLayout()

        # Project dropdown
        self.project_combo = QComboBox()
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        form_layout.addRow("Project:", self.project_combo)

        # Component dropdown (will be populated when project is selected)
        self.component_combo = QComboBox()
        self.component_combo.currentTextChanged.connect(self.on_component_changed)
        form_layout.addRow("Component:", self.component_combo)

        group.setLayout(form_layout)
        layout.addWidget(group)

    def setup_auto_filled_section(self, layout):
        """Setup auto-filled read-only section"""
        group = QGroupBox("ℹ️ AUTO-FILLED PROJECT INFO")
        group.setFont(QFont("Arial", 11, QFont.Bold))
        group.setStyleSheet("QGroupBox { color: #7f8c8d; }")

        form_layout = QFormLayout()

        # Read-only fields
        readonly_style = "QLineEdit { background-color: #34495e; color: #ecf0f1; border: 1px solid #7f8c8d; }"

        self.auto_component_name = QLineEdit()
        self.auto_component_name.setReadOnly(True)
        self.auto_component_name.setStyleSheet(readonly_style)
        form_layout.addRow("Component Name:", self.auto_component_name)

        self.auto_developer = QLineEdit()
        self.auto_developer.setReadOnly(True)
        self.auto_developer.setStyleSheet(readonly_style)
        form_layout.addRow("Developer:", self.auto_developer)

        self.auto_environment = QLineEdit()
        self.auto_environment.setReadOnly(True)
        self.auto_environment.setStyleSheet(readonly_style)
        form_layout.addRow("Environment:", self.auto_environment)

        self.auto_build_server = QLineEdit()
        self.auto_build_server.setReadOnly(True)
        self.auto_build_server.setStyleSheet(readonly_style)
        form_layout.addRow("Build Server:", self.auto_build_server)

        self.auto_deploy_server = QLineEdit()
        self.auto_deploy_server.setReadOnly(True)
        self.auto_deploy_server.setStyleSheet(readonly_style)
        form_layout.addRow("Deploy Server:", self.auto_deploy_server)

        self.auto_database = QLineEdit()
        self.auto_database.setReadOnly(True)
        self.auto_database.setStyleSheet(readonly_style)
        form_layout.addRow("Database:", self.auto_database)

        self.auto_vcs_url = QLineEdit()
        self.auto_vcs_url.setReadOnly(True)
        self.auto_vcs_url.setStyleSheet(readonly_style)
        form_layout.addRow("VCS URL:", self.auto_vcs_url)

        group.setLayout(form_layout)
        layout.addWidget(group)

    def setup_user_input_section(self, layout):
        """Setup user input section"""
        group = QGroupBox("📝 DEPLOYMENT DETAILS")
        group.setFont(QFont("Arial", 11, QFont.Bold))

        form_layout = QFormLayout()

        # JIRA Patch ID
        self.jira_patch = QLineEdit()
        self.jira_patch.setPlaceholderText("e.g., PROJ-123 (optional)")
        form_layout.addRow("JIRA PATCH ID:", self.jira_patch)

        # Timestamp with quick buttons
        timestamp_layout = QHBoxLayout()

        self.timestamp_edit = QDateTimeEdit()
        self.timestamp_edit.setDateTime(QDateTime.currentDateTime())
        self.timestamp_edit.setDisplayFormat("dd-MMM-yyyy h:mmAP")
        self.timestamp_edit.setCalendarPopup(True)
        timestamp_layout.addWidget(self.timestamp_edit)

        now_btn = QPushButton("Now")
        now_btn.setFixedWidth(60)
        now_btn.clicked.connect(lambda: self.timestamp_edit.setDateTime(QDateTime.currentDateTime()))
        timestamp_layout.addWidget(now_btn)

        form_layout.addRow("Timestamp:", timestamp_layout)

        # Database Script
        db_script_layout = QHBoxLayout()

        self.use_db_script_yes = QRadioButton("Yes")
        self.use_db_script_no = QRadioButton("No")
        self.use_db_script_no.setChecked(True)

        db_script_layout.addWidget(QLabel("DB Script?"))
        db_script_layout.addWidget(self.use_db_script_yes)
        db_script_layout.addWidget(self.use_db_script_no)

        self.db_script = QLineEdit()
        self.db_script.setPlaceholderText("Script name")
        self.db_script.setEnabled(False)
        db_script_layout.addWidget(self.db_script)

        self.use_db_script_yes.toggled.connect(lambda: self.db_script.setEnabled(self.use_db_script_yes.isChecked()))

        form_layout.addRow("", db_script_layout)

        # Status checkboxes
        status_layout = QHBoxLayout()

        self.build_success = QCheckBox("Build Success")
        self.build_success.setChecked(True)
        status_layout.addWidget(self.build_success)

        self.deploy_success = QCheckBox("Deploy Success")
        self.deploy_success.setChecked(True)
        status_layout.addWidget(self.deploy_success)

        form_layout.addRow("Status:", status_layout)

        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        self.notes.setPlaceholderText("Optional deployment notes...")
        form_layout.addRow("Notes:", self.notes)

        # Deployed By (dropdown from library)
        deployed_by_layout = QHBoxLayout()
        self.deployed_by_combo = QComboBox()
        self.deployed_by_combo.setEditable(True)
        self.load_deployed_by()
        deployed_by_layout.addWidget(self.deployed_by_combo)

        refresh_deployed_btn = QPushButton("🔄")
        refresh_deployed_btn.setFixedWidth(40)
        refresh_deployed_btn.setToolTip("Refresh from Library")
        refresh_deployed_btn.clicked.connect(self.load_deployed_by)
        deployed_by_layout.addWidget(refresh_deployed_btn)

        form_layout.addRow("Deployed By:", deployed_by_layout)

        group.setLayout(form_layout)
        layout.addWidget(group)

    def setup_buttons_section(self, layout):
        """Setup buttons section - all in one place"""
        group = QGroupBox("💾 SAVE & COPY ACTIONS")
        group.setFont(QFont("Arial", 11, QFont.Bold))

        btn_layout = QVBoxLayout()

        # First row: Save button
        save_btn = QPushButton("💾 SAVE DEPLOYMENT")
        save_btn.setFont(QFont("Arial", 12, QFont.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_btn.clicked.connect(self.save_deployment)
        btn_layout.addWidget(save_btn)

        # Second row: Copy buttons (initially disabled)
        copy_layout = QHBoxLayout()

        self.copy_jira_btn = QPushButton("📋 Copy JIRA")
        self.copy_jira_btn.setFont(QFont("Arial", 11))
        self.copy_jira_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.copy_jira_btn.setEnabled(False)
        self.copy_jira_btn.clicked.connect(self.copy_to_jira)
        copy_layout.addWidget(self.copy_jira_btn)

        self.copy_teams_btn = QPushButton("💬 Copy Teams")
        self.copy_teams_btn.setFont(QFont("Arial", 11))
        self.copy_teams_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #bb8fce;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.copy_teams_btn.setEnabled(False)
        self.copy_teams_btn.clicked.connect(self.copy_to_teams)
        copy_layout.addWidget(self.copy_teams_btn)

        self.copy_both_btn = QPushButton("📋💬 Copy Both")
        self.copy_both_btn.setFont(QFont("Arial", 11))
        self.copy_both_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f39c12;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.copy_both_btn.setEnabled(False)
        self.copy_both_btn.clicked.connect(self.copy_both)
        copy_layout.addWidget(self.copy_both_btn)

        btn_layout.addLayout(copy_layout)

        group.setLayout(btn_layout)
        layout.addWidget(group)

    def load_projects(self):
        """Load projects into dropdown"""
        try:
            projects = self.json_manager.get_all_projects()
            self.project_combo.clear()
            self.project_combo.addItem("-- Select Project --")
            self.project_combo.addItems(sorted(projects))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load projects: {str(e)}")

    def load_deployed_by(self):
        """Load deployed by from library (same as developers)"""
        self.deployed_by_combo.clear()
        developers = self.library_manager.get_developers()
        self.deployed_by_combo.addItems(developers)

        # Set default from settings
        default_deployed_by = get_setting('deployed_by_default', '')
        if default_deployed_by:
            index = self.deployed_by_combo.findText(default_deployed_by)
            if index >= 0:
                self.deployed_by_combo.setCurrentIndex(index)
            else:
                self.deployed_by_combo.setEditText(default_deployed_by)

    def on_project_changed(self, project_name):
        """Handle project selection"""
        if project_name == "-- Select Project --":
            self.clear_fields()
            self.component_combo.clear()
            return

        self.current_project_data = self.json_manager.load_project(project_name)
        if not self.current_project_data:
            return

        # Load components into dropdown
        self.load_components()

        # Update project-level auto-filled fields
        self.auto_environment.setText(self.current_project_data.get('environment', ''))
        self.auto_build_server.setText(self.current_project_data.get('build_server', ''))
        self.auto_deploy_server.setText(self.current_project_data.get('deploy_server', ''))
        self.auto_database.setText(self.current_project_data.get('db_name', ''))

    def load_components(self):
        """Load components for selected project"""
        self.component_combo.clear()
        self.component_combo.addItem("-- Select Component --")

        if not self.current_project_data:
            return

        # Get enabled components
        components = self.json_manager.get_enabled_components(self.project_combo.currentText())

        for component in components:
            component_name = component.get('component_name', '')
            self.component_combo.addItem(component_name, component)  # Store component data in item

    def on_component_changed(self, component_name):
        """Handle component selection"""
        if component_name == "-- Select Component --":
            self.clear_component_fields()
            return

        # Get component data
        index = self.component_combo.currentIndex()
        self.current_component_data = self.component_combo.itemData(index)

        if not self.current_component_data:
            return

        # Update component-specific auto-filled fields
        self.auto_component_name.setText(self.current_component_data.get('component_name', ''))
        self.auto_developer.setText(self.current_component_data.get('developer_name', ''))
        self.auto_vcs_url.setText(self.current_component_data.get('vcs_url', ''))

    def clear_fields(self):
        """Clear all auto-filled fields"""
        self.auto_component_name.clear()
        self.auto_developer.clear()
        self.auto_environment.clear()
        self.auto_build_server.clear()
        self.auto_deploy_server.clear()
        self.auto_database.clear()
        self.auto_vcs_url.clear()

    def clear_component_fields(self):
        """Clear component-specific fields"""
        self.auto_component_name.clear()
        self.auto_developer.clear()
        self.auto_vcs_url.clear()

    def save_deployment(self):
        """Save deployment to Excel"""
        # Validate
        if self.project_combo.currentText() == "-- Select Project --":
            QMessageBox.warning(self, "Validation Error", "Please select a project!")
            return

        if self.component_combo.currentText() == "-- Select Component --":
            QMessageBox.warning(self, "Validation Error", "Please select a component!")
            return

        if not self.deployed_by_combo.currentText().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter 'Deployed By'!")
            return

        # Prepare deployment data
        jira_id = self.jira_patch.text().strip() if self.jira_patch.text().strip() else 'N/A'
        db_script = self.db_script.text().strip() if self.use_db_script_yes.isChecked() else 'N/A'

        # Get timestamp and format date as YYYYMMDD for backup folders
        timestamp_str = self.timestamp_edit.dateTime().toString("dd-MMM-yyyy h:mmAP")
        date_folder = self.timestamp_edit.dateTime().toString("yyyyMMdd")  # Format: 20251109

        # Build backup location with date folder
        base_backup_location = self.current_project_data.get('backup_location', '')
        backup_location_with_date = f"{base_backup_location}\\{date_folder}" if base_backup_location else ''

        # Database backup location with date and filename (only if db script is available)
        base_db_backup = self.current_project_data.get('db_backup_location', '')
        database_name = self.current_project_data.get('db_name', '')

        if self.use_db_script_yes.isChecked() and base_db_backup and database_name:
            # Format: C:\Path\Q_ADIB_MIG_20251109.bak
            db_backup_with_date = f"{base_db_backup}\\{database_name}_{date_folder}.bak"
        else:
            # If no database script, keep the base path only
            db_backup_with_date = base_db_backup

        deployment_data = {
            'jira_patch_id': jira_id,
            'timestamp': timestamp_str,
            'project_name': self.project_combo.currentText(),
            'component_name': self.current_component_data.get('component_name', ''),
            'component_url': self.current_component_data.get('component_url', ''),
            'environment': self.current_project_data.get('environment', ''),
            'vcs_url': self.current_component_data.get('vcs_url', ''),
            'developer_name': self.current_component_data.get('developer_name', ''),
            'build_server': self.current_project_data.get('build_server', ''),
            'deploy_server': self.current_project_data.get('deploy_server', ''),
            'database_name': database_name,
            'db_backup_location': db_backup_with_date,
            'database_script': db_script,
            'backup_location': backup_location_with_date,
            'build_status': self.build_success.isChecked(),
            'deploy_status': self.deploy_success.isChecked(),
            'notes': self.notes.toPlainText(),
            'deployed_by': self.deployed_by_combo.currentText().strip()
        }

        # Check for duplicates
        is_duplicate, duplicate_details = self.excel_manager.check_duplicate_deployment(
            self.project_combo.currentText(),
            deployment_data
        )

        if is_duplicate:
            reply = QMessageBox.question(
                self,
                "Duplicate Detected",
                f"A similar deployment was found:\n\n"
                f"JIRA ID: {duplicate_details.get('jira_id', 'N/A')}\n"
                f"Timestamp: {duplicate_details.get('timestamp', 'N/A')}\n"
                f"Reason: {duplicate_details.get('reason', '')}\n\n"
                f"Do you want to save anyway?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        # Save to Excel
        if self.excel_manager.add_deployment(self.project_combo.currentText(), deployment_data):
            # Store for copy buttons
            self.last_saved_data = deployment_data

            # Enable copy buttons
            self.copy_jira_btn.setEnabled(True)
            self.copy_teams_btn.setEnabled(True)
            self.copy_both_btn.setEnabled(True)

            QMessageBox.information(
                self,
                "Success",
                "✅ Deployment saved successfully!\n\nYou can now use the Copy buttons below."
            )

            # Clear form for next entry (keep project, component, deployed by)
            self.jira_patch.clear()
            self.timestamp_edit.setDateTime(QDateTime.currentDateTime())
            self.use_db_script_no.setChecked(True)
            self.db_script.clear()
            self.notes.clear()

        else:
            QMessageBox.critical(self, "Error", "Failed to save deployment!")

    def copy_to_jira(self):
        """Copy JIRA format to clipboard"""
        if not self.last_saved_data:
            QMessageBox.warning(self, "No Data", "Please save a deployment first!")
            return

        jira_msg = JiraFormatter.format(self.last_saved_data)
        clipboard = QApplication.clipboard()
        clipboard.setText(jira_msg)

        QMessageBox.information(self, "Copied!", "📋 JIRA format copied to clipboard!")

    def copy_to_teams(self):
        """Copy Teams format to clipboard"""
        if not self.last_saved_data:
            QMessageBox.warning(self, "No Data", "Please save a deployment first!")
            return

        teams_msg = TeamsFormatter.format(self.last_saved_data)
        clipboard = QApplication.clipboard()
        clipboard.setText(teams_msg)

        QMessageBox.information(self, "Copied!", "💬 Teams format copied to clipboard!")

    def copy_both(self):
        """Copy both formats to clipboard"""
        if not self.last_saved_data:
            QMessageBox.warning(self, "No Data", "Please save a deployment first!")
            return

        jira_msg = JiraFormatter.format(self.last_saved_data)
        teams_msg = TeamsFormatter.format(self.last_saved_data)

        combined = f"{jira_msg}\n\n{'='*50}\n\n{teams_msg}"
        clipboard = QApplication.clipboard()
        clipboard.setText(combined)

        QMessageBox.information(self, "Copied!", "📋💬 Both formats copied to clipboard!")
