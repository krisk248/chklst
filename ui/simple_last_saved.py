"""
Last Saved Deployments Tab
View recently saved deployments and copy to JIRA/Teams anytime
"""

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox,
    QHeaderView, QSplitter, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication

from utils.excel_manager import ExcelManager
from utils.integration_formatter import JiraFormatter, TeamsFormatter


class LastSavedTab(QWidget):
    """Tab showing last saved deployments with copy functionality"""

    def __init__(self):
        super().__init__()
        self.excel_manager = ExcelManager()
        self.selected_deployment = None

        self.init_ui()
        self.refresh_deployments()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("📋 LAST SAVED DEPLOYMENTS")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #ecf0f1; margin: 10px;")
        layout.addWidget(title)

        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_deployments)
        refresh_layout.addWidget(refresh_btn)

        layout.addLayout(refresh_layout)

        # Create splitter for table and details
        splitter = QSplitter(Qt.Vertical)

        # Deployments table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #555;
                background-color: #2b2b2b;
                color: #ecf0f1;
                alternate-background-color: #333;
            }
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: 1px solid #555;
                font-weight: bold;
            }
        """)

        # Set headers
        headers = ["Timestamp", "JIRA ID", "Project", "Component", "Environment", "Deployed By"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 100)

        splitter.addWidget(self.table)

        # Details and copy section
        details_widget = QWidget()
        details_layout = QVBoxLayout()

        # Details group
        details_group = QGroupBox("📝 Deployment Details")
        details_group.setFont(QFont("Arial", 11, QFont.Bold))
        details_group_layout = QVBoxLayout()

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
                color: #ecf0f1;
                font-size: 12px;
            }
        """)
        details_group_layout.addWidget(self.details_text)

        details_group.setLayout(details_group_layout)
        details_layout.addWidget(details_group)

        # Copy buttons
        copy_layout = QHBoxLayout()

        self.copy_jira_btn = QPushButton("📋 Copy for JIRA")
        self.copy_jira_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.copy_jira_btn.setEnabled(False)
        self.copy_jira_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover:enabled {
                background-color: #5dade2;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #999;
            }
        """)
        self.copy_jira_btn.clicked.connect(self.copy_jira)

        self.copy_teams_btn = QPushButton("💬 Copy for Teams")
        self.copy_teams_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.copy_teams_btn.setEnabled(False)
        self.copy_teams_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover:enabled {
                background-color: #bb8fce;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #999;
            }
        """)
        self.copy_teams_btn.clicked.connect(self.copy_teams)

        self.copy_both_btn = QPushButton("📋💬 Copy Both")
        self.copy_both_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.copy_both_btn.setEnabled(False)
        self.copy_both_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover:enabled {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #999;
            }
        """)
        self.copy_both_btn.clicked.connect(self.copy_both)

        copy_layout.addWidget(self.copy_jira_btn)
        copy_layout.addWidget(self.copy_teams_btn)
        copy_layout.addWidget(self.copy_both_btn)

        details_layout.addLayout(copy_layout)

        # Info label
        info_label = QLabel("💡 Select a deployment from the table above to view details and copy")
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; font-size: 10px; padding: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        details_layout.addWidget(info_label)

        details_widget.setLayout(details_layout)
        splitter.addWidget(details_widget)

        # Set splitter proportions
        splitter.setSizes([400, 300])

        layout.addWidget(splitter)

        self.setLayout(layout)

    def refresh_deployments(self):
        """Refresh deployments from Excel files"""
        try:
            # Get current month deployments
            now = datetime.now()
            all_deployments = self.excel_manager.get_all_monthly_deployments(now.month, now.year)

            # Flatten and sort by timestamp
            deployment_list = []
            for project_name, deployments in all_deployments.items():
                deployment_list.extend(deployments)

            # Sort by timestamp (newest first)
            deployment_list.sort(
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )

            # Limit to last 50 deployments
            deployment_list = deployment_list[:50]

            # Update table
            self.table.setRowCount(len(deployment_list))

            for row, deployment in enumerate(deployment_list):
                # Store full deployment data in first column
                timestamp_item = QTableWidgetItem(deployment.get('timestamp', ''))
                timestamp_item.setData(Qt.UserRole, deployment)  # Store full data
                self.table.setItem(row, 0, timestamp_item)

                self.table.setItem(row, 1, QTableWidgetItem(deployment.get('jira_patch_id', 'N/A')))
                self.table.setItem(row, 2, QTableWidgetItem(deployment.get('project_name', '')))
                self.table.setItem(row, 3, QTableWidgetItem(deployment.get('component_name', '')))
                self.table.setItem(row, 4, QTableWidgetItem(deployment.get('environment', '')))
                self.table.setItem(row, 5, QTableWidgetItem(deployment.get('deployed_by', '')))

            # Clear selection and details
            self.table.clearSelection()
            self.selected_deployment = None
            self.update_details()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load deployments: {str(e)}")

    def on_selection_changed(self):
        """Handle table selection change"""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            # Get deployment data from first column
            item = self.table.item(row, 0)
            self.selected_deployment = item.data(Qt.UserRole)
            self.update_details()
        else:
            self.selected_deployment = None
            self.update_details()

    def update_details(self):
        """Update details panel and enable/disable buttons"""
        if self.selected_deployment:
            # Enable buttons
            self.copy_jira_btn.setEnabled(True)
            self.copy_teams_btn.setEnabled(True)
            self.copy_both_btn.setEnabled(True)

            # Display details
            details = f"""
╔═══════════════════════════════════════════════════════╗
║           DEPLOYMENT DETAILS                          ║
╚═══════════════════════════════════════════════════════╝

📋 JIRA Patch ID:     {self.selected_deployment.get('jira_patch_id', 'N/A')}
📅 Timestamp:         {self.selected_deployment.get('timestamp', '')}
📁 Project:           {self.selected_deployment.get('project_name', '')}
🔧 Component:         {self.selected_deployment.get('component_name', '')}
🌍 Environment:       {self.selected_deployment.get('environment', '')}

👤 Developer:         {self.selected_deployment.get('developer_name', '')}
👤 Deployed By:       {self.selected_deployment.get('deployed_by', '')}

🏗️  Build Server:     {self.selected_deployment.get('build_server', '')}
🚀 Deploy Server:     {self.selected_deployment.get('deploy_server', '')}

💾 Database:          {self.selected_deployment.get('database_name', '')}
📝 DB Script:         {self.selected_deployment.get('database_script', 'N/A')}
💾 Backup Location:   {self.selected_deployment.get('backup_location', '')}

🔨 Build Status:      {"✅ Success" if self.selected_deployment.get('build_status') else "❌ Failed"}
🚀 Deploy Status:     {"✅ Success" if self.selected_deployment.get('deploy_status') else "❌ Failed"}

📝 Notes:
{self.selected_deployment.get('notes', 'No notes')}

🔗 VCS URL:
{self.selected_deployment.get('vcs_url', '')}
            """
            self.details_text.setPlainText(details)
        else:
            # Disable buttons
            self.copy_jira_btn.setEnabled(False)
            self.copy_teams_btn.setEnabled(False)
            self.copy_both_btn.setEnabled(False)

            # Clear details
            self.details_text.setPlainText("No deployment selected.\n\nSelect a deployment from the table above to view details.")

    def copy_jira(self):
        """Copy selected deployment for JIRA"""
        if not self.selected_deployment:
            return

        try:
            formatted_text = JiraFormatter.format(self.selected_deployment)
            clipboard = QApplication.clipboard()
            clipboard.setText(formatted_text)

            QMessageBox.information(
                self,
                "Copied!",
                "Deployment info copied to clipboard in JIRA format!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy: {str(e)}")

    def copy_teams(self):
        """Copy selected deployment for Teams"""
        if not self.selected_deployment:
            return

        try:
            formatted_text = TeamsFormatter.format(self.selected_deployment)
            clipboard = QApplication.clipboard()
            clipboard.setText(formatted_text)

            QMessageBox.information(
                self,
                "Copied!",
                "Deployment info copied to clipboard in Teams format!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy: {str(e)}")

    def copy_both(self):
        """Copy selected deployment for both JIRA and Teams"""
        if not self.selected_deployment:
            return

        try:
            jira_text = JiraFormatter.format(self.selected_deployment)
            teams_text = TeamsFormatter.format(self.selected_deployment)

            combined_text = f"""=== JIRA FORMAT ===
{jira_text}

=== TEAMS FORMAT ===
{teams_text}"""

            clipboard = QApplication.clipboard()
            clipboard.setText(combined_text)

            QMessageBox.information(
                self,
                "Copied!",
                "Deployment info copied to clipboard in both JIRA and Teams formats!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy: {str(e)}")


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = LastSavedTab()
    window.show()
    sys.exit(app.exec_())
