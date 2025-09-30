"""
Simple Deployment UI with Auto-fill and Time Picker
Clean, minimal interface for deployment tracking
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QComboBox, QLineEdit, QTextEdit, QCheckBox, QPushButton, 
    QRadioButton, QButtonGroup, QGroupBox, QCalendarWidget,
    QTimeEdit, QDateTimeEdit, QMessageBox, QDialog, QSpinBox,
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QDateTime, QTime
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QApplication
from utils.json_manager import ProjectJSONManager
from utils.excel_manager import ExcelManager
from utils.integration_formatter import JiraFormatter, TeamsFormatter


class TimePickerDialog(QDialog):
    """Custom time picker dialog with quick preset buttons"""
    
    def __init__(self, current_datetime=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date & Time")
        self.setModal(True)
        self.setFixedSize(400, 350)
        
        if current_datetime is None:
            current_datetime = QDateTime.currentDateTime()
        
        self.selected_datetime = current_datetime
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Calendar widget
        calendar_label = QLabel("Select Date:")
        calendar_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(calendar_label)
        
        self.calendar = QCalendarWidget()
        self.calendar.setSelectedDate(self.selected_datetime.date())
        self.calendar.clicked.connect(self.date_changed)
        layout.addWidget(self.calendar)
        
        # Time section
        time_label = QLabel("Select Time:")
        time_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(time_label)
        
        time_layout = QHBoxLayout()
        
        # Time edit
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(self.selected_datetime.time())
        self.time_edit.setDisplayFormat("hh:mm:ss")
        self.time_edit.timeChanged.connect(self.time_changed)
        time_layout.addWidget(self.time_edit)
        
        # Quick time buttons
        quick_times = [
            ("Now", None),
            ("09:00", QTime(9, 0)),
            ("12:00", QTime(12, 0)),
            ("17:00", QTime(17, 0))
        ]
        
        for label, time_val in quick_times:
            btn = QPushButton(label)
            if time_val is None:
                btn.clicked.connect(self.set_current_time)
            else:
                btn.clicked.connect(lambda checked, t=time_val: self.set_time(t))
            time_layout.addWidget(btn)
            
        layout.addLayout(time_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def date_changed(self, date):
        """Handle date change"""
        self.selected_datetime.setDate(date)
        
    def time_changed(self, time):
        """Handle time change"""
        self.selected_datetime.setTime(time)
        
    def set_current_time(self):
        """Set to current time"""
        current_time = QTime.currentTime()
        self.time_edit.setTime(current_time)
        self.selected_datetime.setTime(current_time)
        
    def set_time(self, time):
        """Set specific time"""
        self.time_edit.setTime(time)
        self.selected_datetime.setTime(time)
        
    def get_datetime(self):
        """Get selected datetime"""
        return self.selected_datetime


class SimpleDeploymentForm(QWidget):
    """Simple deployment form with auto-fill from JSON"""
    
    def __init__(self):
        super().__init__()
        self.json_manager = ProjectJSONManager()
        self.excel_manager = ExcelManager()
        
        self.projects_data = {}
        self.current_project_data = None
        self.current_component_data = None
        
        self.init_ui()
        self.load_projects()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Deployment Tracker")
        
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        main_widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QLabel("📋 DEPLOYMENT FORM")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # Project Selection Section
        self.setup_project_selection(layout)
        
        # Auto-filled Section
        self.setup_auto_filled_section(layout)
        
        # User Input Section
        self.setup_user_input_section(layout)

        # Button Section
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Save Button
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
        button_layout.addWidget(save_btn)

        # Copy to JIRA Button
        jira_btn = QPushButton("📋 Copy for JIRA")
        jira_btn.setFont(QFont("Arial", 12, QFont.Bold))
        jira_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        jira_btn.clicked.connect(self.copy_to_jira)
        button_layout.addWidget(jira_btn)

        # Copy to Teams Button
        teams_btn = QPushButton("💬 Copy for Teams")
        teams_btn.setFont(QFont("Arial", 12, QFont.Bold))
        teams_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #bb8fce;
            }
        """)
        teams_btn.clicked.connect(self.copy_to_teams)
        button_layout.addWidget(teams_btn)

        layout.addLayout(button_layout)
        
        layout.addStretch()
        main_widget.setLayout(layout)
        scroll.setWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        
    def setup_project_selection(self, layout):
        """Setup project and component selection"""
        group = QGroupBox("📁 Project Selection")
        group.setFont(QFont("Arial", 11, QFont.Bold))
        group.setStyleSheet("QGroupBox { color: #34495e; }")
        
        form_layout = QFormLayout()
        
        # Project dropdown
        self.project_combo = QComboBox()
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        form_layout.addRow("Project:", self.project_combo)
        
        # Component radio buttons
        component_layout = QHBoxLayout()
        self.component_group = QButtonGroup()
        
        self.frontend_radio = QRadioButton("Frontend")
        self.backend_radio = QRadioButton("Backend")
        self.backoffice_radio = QRadioButton("Backoffice")
        
        self.component_group.addButton(self.frontend_radio, 0)
        self.component_group.addButton(self.backend_radio, 1)
        self.component_group.addButton(self.backoffice_radio, 2)
        
        self.frontend_radio.toggled.connect(self.on_component_changed)
        self.backend_radio.toggled.connect(self.on_component_changed)
        self.backoffice_radio.toggled.connect(self.on_component_changed)
        
        component_layout.addWidget(self.frontend_radio)
        component_layout.addWidget(self.backend_radio)
        component_layout.addWidget(self.backoffice_radio)
        
        form_layout.addRow("Component:", component_layout)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        
    def setup_auto_filled_section(self, layout):
        """Setup auto-filled read-only section"""
        group = QGroupBox("🔒 Auto-filled from Project Configuration")
        group.setFont(QFont("Arial", 11, QFont.Bold))
        group.setStyleSheet("QGroupBox { color: #7f8c8d; }")
        
        form_layout = QFormLayout()
        
        # Read-only fields
        self.auto_environment = QLineEdit()
        self.auto_environment.setReadOnly(True)
        self.auto_environment.setStyleSheet("QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; }")
        
        self.auto_developer = QLineEdit()
        self.auto_developer.setReadOnly(True)
        self.auto_developer.setStyleSheet("QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; }")
        
        self.auto_build_server = QLineEdit()
        self.auto_build_server.setReadOnly(True)
        self.auto_build_server.setStyleSheet("QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; }")
        
        self.auto_deploy_server = QLineEdit()
        self.auto_deploy_server.setReadOnly(True)
        self.auto_deploy_server.setStyleSheet("QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; }")
        
        self.auto_database = QLineEdit()
        self.auto_database.setReadOnly(True)
        self.auto_database.setStyleSheet("QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; }")
        
        self.auto_backup_path = QLineEdit()
        self.auto_backup_path.setReadOnly(True)
        self.auto_backup_path.setStyleSheet("QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; }")
        
        self.auto_vcs_url = QLineEdit()
        self.auto_vcs_url.setReadOnly(True)
        self.auto_vcs_url.setStyleSheet("QLineEdit { background-color: #2c3e50; color: white; border: 1px solid #34495e; }")
        
        form_layout.addRow("Environment:", self.auto_environment)
        form_layout.addRow("Developer:", self.auto_developer)
        form_layout.addRow("Build Server:", self.auto_build_server)
        form_layout.addRow("Deploy Server:", self.auto_deploy_server)
        form_layout.addRow("Database:", self.auto_database)
        form_layout.addRow("Backup Path:", self.auto_backup_path)
        form_layout.addRow("VCS URL:", self.auto_vcs_url)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        
    def setup_user_input_section(self, layout):
        """Setup user input section"""
        group = QGroupBox("✏️ User Input Required")
        group.setFont(QFont("Arial", 11, QFont.Bold))
        group.setStyleSheet("QGroupBox { color: #2c3e50; }")
        
        form_layout = QFormLayout()
        
        # JIRA Patch ID
        self.jira_patch = QLineEdit()
        self.jira_patch.setPlaceholderText("Enter JIRA ticket number (optional)")
        form_layout.addRow("JIRA PATCH ID:", self.jira_patch)
        
        # Timestamp with time picker
        timestamp_layout = QHBoxLayout()
        
        self.timestamp_edit = QDateTimeEdit()
        self.timestamp_edit.setDateTime(QDateTime.currentDateTime())
        self.timestamp_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.timestamp_edit.setCalendarPopup(True)
        timestamp_layout.addWidget(self.timestamp_edit)
        
        now_btn = QPushButton("NOW")
        now_btn.setMaximumWidth(60)
        now_btn.clicked.connect(self.set_current_time)
        timestamp_layout.addWidget(now_btn)
        
        calendar_btn = QPushButton("📅")
        calendar_btn.setMaximumWidth(40)
        calendar_btn.clicked.connect(self.open_time_picker)
        timestamp_layout.addWidget(calendar_btn)
        
        time_btn = QPushButton("🕐")
        time_btn.setMaximumWidth(40)
        time_btn.clicked.connect(self.open_time_picker)
        timestamp_layout.addWidget(time_btn)
        
        form_layout.addRow("Timestamp:", timestamp_layout)
        
        # Database Script
        self.db_script = QLineEdit()
        self.db_script.setPlaceholderText("Enter DB script name (optional)")
        form_layout.addRow("Database Script:", self.db_script)
        
        # Status checkboxes
        status_layout = QHBoxLayout()
        
        self.build_success = QCheckBox("Build Successful")
        self.build_success.setChecked(True)
        status_layout.addWidget(self.build_success)
        
        self.deploy_success = QCheckBox("Deploy Successful")
        self.deploy_success.setChecked(True)
        status_layout.addWidget(self.deploy_success)
        
        form_layout.addRow("Status:", status_layout)
        
        # Notes
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(100)
        self.notes.setPlaceholderText("Enter deployment notes...")
        form_layout.addRow("Notes:", self.notes)
        
        # Deployed By
        self.deployed_by = QLineEdit()
        self.deployed_by.setPlaceholderText("Enter your name")
        form_layout.addRow("Deployed By:", self.deployed_by)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        
    def load_projects(self):
        """Load projects from JSON files"""
        try:
            projects = self.json_manager.get_all_projects()
            self.project_combo.clear()
            self.project_combo.addItem("-- Select Project --")
            
            for project_name in projects:
                project_data = self.json_manager.load_project(project_name)
                if project_data:
                    self.projects_data[project_name] = project_data
                    self.project_combo.addItem(project_name)
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load projects: {str(e)}")
            
    def on_project_changed(self, project_name):
        """Handle project selection change"""
        if project_name == "-- Select Project --":
            self.clear_auto_fields()
            self.disable_components()
            return
            
        if project_name in self.projects_data:
            self.current_project_data = self.projects_data[project_name]
            self.update_auto_fields_from_project()
            self.enable_components()
            
            # Auto-select first enabled component
            components = self.current_project_data.get('components', {})
            for comp_name, comp_data in components.items():
                if comp_data.get('enabled', False):
                    if comp_name == 'frontend':
                        self.frontend_radio.setChecked(True)
                    elif comp_name == 'backend':
                        self.backend_radio.setChecked(True)
                    elif comp_name == 'backoffice':
                        self.backoffice_radio.setChecked(True)
                    break
                    
    def on_component_changed(self):
        """Handle component selection change"""
        if not self.current_project_data:
            return
            
        selected_component = None
        if self.frontend_radio.isChecked():
            selected_component = 'frontend'
        elif self.backend_radio.isChecked():
            selected_component = 'backend'
        elif self.backoffice_radio.isChecked():
            selected_component = 'backoffice'
            
        if selected_component:
            components = self.current_project_data.get('components', {})
            self.current_component_data = components.get(selected_component, {})
            self.update_auto_fields_from_component()
            
    def update_auto_fields_from_project(self):
        """Update auto-filled fields from project data"""
        if not self.current_project_data:
            return
            
        self.auto_environment.setText(self.current_project_data.get('environment', 'QA'))
        self.auto_build_server.setText(self.current_project_data.get('build_server', ''))
        self.auto_deploy_server.setText(self.current_project_data.get('deploy_server', ''))
        self.auto_database.setText(self.current_project_data.get('db_name', ''))
        self.auto_backup_path.setText(self.current_project_data.get('backup_location', ''))
        
    def update_auto_fields_from_component(self):
        """Update auto-filled fields from component data"""
        if not self.current_component_data:
            return
            
        self.auto_developer.setText(self.current_component_data.get('developer_name', ''))
        self.auto_vcs_url.setText(self.current_component_data.get('vcs_url', ''))
        
    def clear_auto_fields(self):
        """Clear all auto-filled fields"""
        self.auto_environment.clear()
        self.auto_developer.clear()
        self.auto_build_server.clear()
        self.auto_deploy_server.clear()
        self.auto_database.clear()
        self.auto_backup_path.clear()
        self.auto_vcs_url.clear()
        
    def enable_components(self):
        """Enable component radio buttons"""
        if not self.current_project_data:
            return
            
        components = self.current_project_data.get('components', {})
        
        # Enable/disable based on component enabled status
        self.frontend_radio.setEnabled(components.get('frontend', {}).get('enabled', False))
        self.backend_radio.setEnabled(components.get('backend', {}).get('enabled', False))
        self.backoffice_radio.setEnabled(components.get('backoffice', {}).get('enabled', False))
        
    def disable_components(self):
        """Disable component radio buttons"""
        self.frontend_radio.setEnabled(False)
        self.backend_radio.setEnabled(False)
        self.backoffice_radio.setEnabled(False)
        
        # Clear selection
        self.component_group.setExclusive(False)
        self.frontend_radio.setChecked(False)
        self.backend_radio.setChecked(False)
        self.backoffice_radio.setChecked(False)
        self.component_group.setExclusive(True)
        
    def set_current_time(self):
        """Set timestamp to current time"""
        self.timestamp_edit.setDateTime(QDateTime.currentDateTime())
        
    def open_time_picker(self):
        """Open custom time picker dialog"""
        dialog = TimePickerDialog(self.timestamp_edit.dateTime(), self)
        if dialog.exec_() == QDialog.Accepted:
            self.timestamp_edit.setDateTime(dialog.get_datetime())

    def get_current_deployment_data(self):
        """
        Extract current deployment data from form without saving

        Returns:
            dict: Deployment data dictionary or None if validation fails
        """
        # Validate required fields
        if self.project_combo.currentText() == "-- Select Project --":
            QMessageBox.warning(self, "Validation", "Please select a project")
            return None

        if not any([self.frontend_radio.isChecked(), self.backend_radio.isChecked(), self.backoffice_radio.isChecked()]):
            QMessageBox.warning(self, "Validation", "Please select a component")
            return None

        if not self.deployed_by.text().strip():
            QMessageBox.warning(self, "Validation", "Please enter 'Deployed By' name")
            return None

        # Get component name
        component_name = ""
        if self.frontend_radio.isChecked():
            component_name = self.current_component_data.get('component_name', 'Frontend')
        elif self.backend_radio.isChecked():
            component_name = self.current_component_data.get('component_name', 'Backend')
        elif self.backoffice_radio.isChecked():
            component_name = self.current_component_data.get('component_name', 'Backoffice')

        # Prepare deployment data
        deployment_data = {
            'jira_patch_id': self.jira_patch.text().strip() or 'N/A',
            'timestamp': self.timestamp_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss"),
            'project_name': self.project_combo.currentText(),
            'component_name': component_name,
            'environment': self.auto_environment.text(),
            'vcs_url': self.auto_vcs_url.text(),
            'developer_name': self.auto_developer.text(),
            'build_server': self.auto_build_server.text(),
            'deploy_server': self.auto_deploy_server.text(),
            'database_name': self.auto_database.text(),
            'database_script': self.db_script.text().strip() or 'N/A',
            'backup_location': self.auto_backup_path.text(),
            'build_status': self.build_success.isChecked(),
            'deploy_status': self.deploy_success.isChecked(),
            'notes': self.notes.toPlainText().strip(),
            'deployed_by': self.deployed_by.text().strip()
        }

        return deployment_data

    def copy_to_jira(self):
        """Copy deployment data to clipboard in JIRA format"""
        try:
            # Get current deployment data
            deployment_data = self.get_current_deployment_data()
            if not deployment_data:
                return

            # Format for JIRA
            formatted_text = JiraFormatter.format(deployment_data)

            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(formatted_text)

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                "Deployment information copied to clipboard in JIRA format!\n\nYou can now paste it into JIRA."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error copying to JIRA format: {str(e)}")

    def copy_to_teams(self):
        """Copy deployment data to clipboard in Microsoft Teams format"""
        try:
            # Get current deployment data
            deployment_data = self.get_current_deployment_data()
            if not deployment_data:
                return

            # Format for Teams
            formatted_text = TeamsFormatter.format(deployment_data)

            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(formatted_text)

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                "Deployment information copied to clipboard in Microsoft Teams format!\n\nYou can now paste it into Teams."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error copying to Teams format: {str(e)}")

    def save_deployment(self):
        """Save deployment to Excel"""
        try:
            # Validate required fields
            if self.project_combo.currentText() == "-- Select Project --":
                QMessageBox.warning(self, "Validation", "Please select a project")
                return
                
            if not any([self.frontend_radio.isChecked(), self.backend_radio.isChecked(), self.backoffice_radio.isChecked()]):
                QMessageBox.warning(self, "Validation", "Please select a component")
                return
                
            if not self.deployed_by.text().strip():
                QMessageBox.warning(self, "Validation", "Please enter 'Deployed By' name")
                return
                
            # Get component name
            component_name = ""
            if self.frontend_radio.isChecked():
                component_name = self.current_component_data.get('component_name', 'Frontend')
            elif self.backend_radio.isChecked():
                component_name = self.current_component_data.get('component_name', 'Backend')
            elif self.backoffice_radio.isChecked():
                component_name = self.current_component_data.get('component_name', 'Backoffice')
                
            # Prepare deployment data
            deployment_data = {
                'jira_patch_id': self.jira_patch.text().strip() or 'N/A',
                'timestamp': self.timestamp_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss"),
                'project_name': self.project_combo.currentText(),
                'component_name': component_name,
                'environment': self.auto_environment.text(),
                'vcs_url': self.auto_vcs_url.text(),
                'developer_name': self.auto_developer.text(),
                'build_server': self.auto_build_server.text(),
                'deploy_server': self.auto_deploy_server.text(),
                'database_name': self.auto_database.text(),
                'database_script': self.db_script.text().strip() or 'N/A',
                'backup_location': self.auto_backup_path.text(),
                'build_status': self.build_success.isChecked(),
                'deploy_status': self.deploy_success.isChecked(),
                'notes': self.notes.toPlainText().strip(),
                'deployed_by': self.deployed_by.text().strip()
            }
            
            # Save to Excel
            success = self.excel_manager.add_deployment(
                self.project_combo.currentText(),
                deployment_data
            )
            
            if success:
                QMessageBox.information(self, "Success", "Deployment saved successfully!")
                self.clear_form()
            else:
                QMessageBox.warning(self, "Error", "Failed to save deployment")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving deployment: {str(e)}")
            
    def clear_form(self):
        """Clear the form for next entry"""
        self.jira_patch.clear()
        self.timestamp_edit.setDateTime(QDateTime.currentDateTime())
        self.db_script.clear()
        self.build_success.setChecked(True)
        self.deploy_success.setChecked(True)
        self.notes.clear()
        # Keep project, component, and deployed_by for convenience


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = SimpleDeploymentForm()
    window.show()
    sys.exit(app.exec_())