"""
Simple Reports Viewer for Monthly Deployment Data
View, export and analyze deployment reports
"""

import sys
import calendar
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
    QMessageBox, QHeaderView, QTabWidget, QTextEdit,
    QProgressBar, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
import openpyxl
from utils.excel_manager import ExcelManager


class PDFGenerationThread(QThread):
    """Thread for generating PDF reports"""
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)
    
    def __init__(self, month, year, excel_manager):
        super().__init__()
        self.month = month
        self.year = year
        self.excel_manager = excel_manager
        
    def run(self):
        try:
            from utils.pdf_generator import PDFGenerator
            
            self.progress.emit(20)
            pdf_gen = PDFGenerator(self.excel_manager)
            
            self.progress.emit(50)
            output_path = pdf_gen.generate_monthly_report(self.month, self.year)
            
            self.progress.emit(100)
            self.finished.emit(True, output_path)
            
        except Exception as e:
            self.finished.emit(False, str(e))


class SimpleReportsViewer(QWidget):
    """Simple reports viewer with monthly deployment data"""
    
    def __init__(self):
        super().__init__()
        self.excel_manager = ExcelManager()
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.current_data = {}
        
        self.init_ui()
        self.load_current_month_data()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📊 DEPLOYMENT REPORTS")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 10px;")
        layout.addWidget(title)
        
        # Controls section
        self.setup_controls(layout)
        
        # Main content with tabs
        self.setup_main_content(layout)
        
        self.setLayout(layout)
        
    def setup_controls(self, layout):
        """Setup control buttons and dropdowns"""
        controls_group = QGroupBox("📅 Report Selection")
        controls_group.setFont(QFont("Arial", 11, QFont.Bold))
        
        controls_layout = QHBoxLayout()
        
        # Month selection
        controls_layout.addWidget(QLabel("Month:"))
        self.month_combo = QComboBox()
        for i in range(1, 13):
            month_name = calendar.month_name[i]
            self.month_combo.addItem(f"{month_name} ({i:02d})", i)
        self.month_combo.setCurrentIndex(self.current_month - 1)
        self.month_combo.currentIndexChanged.connect(lambda idx: self.on_month_changed(self.month_combo.itemData(idx)))
        controls_layout.addWidget(self.month_combo)
        
        # Year selection
        controls_layout.addWidget(QLabel("Year:"))
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 2):
            self.year_combo.addItem(str(year), year)
        self.year_combo.setCurrentText(str(self.current_year))
        self.year_combo.currentIndexChanged.connect(lambda idx: self.on_year_changed(self.year_combo.itemData(idx)))
        controls_layout.addWidget(self.year_combo)
        
        controls_layout.addStretch()
        
        # Action buttons
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        controls_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📤 Export Excel")
        self.export_btn.clicked.connect(self.export_excel)
        controls_layout.addWidget(self.export_btn)
        
        self.pdf_btn = QPushButton("📋 Generate PDF")
        self.pdf_btn.clicked.connect(self.generate_pdf)
        controls_layout.addWidget(self.pdf_btn)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def setup_main_content(self, layout):
        """Setup main content area with tabs"""
        self.tab_widget = QTabWidget()
        
        # Summary tab
        self.setup_summary_tab()
        
        # Deployments table tab
        self.setup_deployments_tab()
        
        # Statistics tab
        self.setup_statistics_tab()
        
        layout.addWidget(self.tab_widget)
        
    def setup_summary_tab(self):
        """Setup summary tab"""
        summary_widget = QWidget()
        layout = QVBoxLayout()
        
        # Summary cards
        cards_layout = QHBoxLayout()
        
        # Total deployments card
        self.total_card = self.create_summary_card("Total Deployments", "0", "#3498db")
        cards_layout.addWidget(self.total_card)
        
        # Success rate card
        self.success_card = self.create_summary_card("Success Rate", "0%", "#27ae60")
        cards_layout.addWidget(self.success_card)
        
        # Projects card
        self.projects_card = self.create_summary_card("Active Projects", "0", "#e74c3c")
        cards_layout.addWidget(self.projects_card)
        
        layout.addLayout(cards_layout)
        
        # Quick stats text
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(200)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.stats_text)
        
        layout.addStretch()
        summary_widget.setLayout(layout)
        self.tab_widget.addTab(summary_widget, "📈 Summary")
        
    def setup_deployments_tab(self):
        """Setup deployments table tab"""
        deployments_widget = QWidget()
        layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Project:"))
        
        self.project_filter = QComboBox()
        self.project_filter.addItem("All Projects")
        self.project_filter.currentTextChanged.connect(self.filter_deployments)
        filter_layout.addWidget(self.project_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Deployments table
        self.deployments_table = QTableWidget()
        self.deployments_table.setAlternatingRowColors(True)
        self.deployments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.deployments_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Set headers
        headers = [
            "JIRA ID", "Timestamp", "Project", "Component", "Environment",
            "Developer", "Build Status", "Deploy Status", "Notes"
        ]
        self.deployments_table.setColumnCount(len(headers))
        self.deployments_table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        header = self.deployments_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i, width in enumerate([100, 150, 120, 120, 80, 120, 100, 100, 200]):
            if i < len(headers) - 1:  # Don't set width for last column (it stretches)
                self.deployments_table.setColumnWidth(i, width)
        
        layout.addWidget(self.deployments_table)
        
        deployments_widget.setLayout(layout)
        self.tab_widget.addTab(deployments_widget, "📋 Deployments")
        
    def setup_statistics_tab(self):
        """Setup statistics tab"""
        stats_widget = QWidget()
        layout = QVBoxLayout()
        
        # Component breakdown
        component_group = QGroupBox("Component Breakdown")
        component_layout = QVBoxLayout()
        
        self.component_stats = QTextEdit()
        self.component_stats.setReadOnly(True)
        self.component_stats.setMaximumHeight(150)
        component_layout.addWidget(self.component_stats)
        
        component_group.setLayout(component_layout)
        layout.addWidget(component_group)
        
        # Project breakdown
        project_group = QGroupBox("Project Breakdown")
        project_layout = QVBoxLayout()
        
        self.project_stats = QTextEdit()
        self.project_stats.setReadOnly(True)
        self.project_stats.setMaximumHeight(150)
        project_layout.addWidget(self.project_stats)
        
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # Success/Failure analysis
        success_group = QGroupBox("Success/Failure Analysis")
        success_layout = QVBoxLayout()
        
        self.success_stats = QTextEdit()
        self.success_stats.setReadOnly(True)
        self.success_stats.setMaximumHeight(150)
        success_layout.addWidget(self.success_stats)
        
        success_group.setLayout(success_layout)
        layout.addWidget(success_group)
        
        layout.addStretch()
        stats_widget.setLayout(layout)
        self.tab_widget.addTab(stats_widget, "📊 Statistics")
        
    def create_summary_card(self, title, value, color):
        """Create a summary card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: #666;")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        card.setLayout(layout)
        
        # Store value label for updates
        setattr(card, 'value_label', value_label)
        
        return card
        
    def on_month_changed(self, month):
        """Handle month change"""
        self.current_month = month
        self.load_current_month_data()
        
    def on_year_changed(self, year):
        """Handle year change"""
        self.current_year = year
        self.load_current_month_data()
        
    def refresh_data(self):
        """Refresh current data"""
        self.load_current_month_data()
        
    def load_current_month_data(self):
        """Load data for current month/year"""
        try:
            # Get all deployments for the month
            self.current_data = self.excel_manager.get_all_monthly_deployments(
                self.current_month, self.current_year
            )
            
            # Update UI
            self.update_summary()
            self.update_deployments_table()
            self.update_statistics()
            self.update_project_filter()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load data: {str(e)}")
            
    def update_summary(self):
        """Update summary cards"""
        stats = self.excel_manager.get_deployment_stats(self.current_month, self.current_year)
        
        # Update cards
        self.total_card.value_label.setText(str(stats['total_deployments']))
        
        success_rate = stats.get('deploy_success_rate', 0)
        self.success_card.value_label.setText(f"{success_rate:.1f}%")
        
        project_count = len(stats.get('project_counts', {}))
        self.projects_card.value_label.setText(str(project_count))
        
        # Update stats text
        stats_text = f"""
Monthly Deployment Summary - {calendar.month_name[self.current_month]} {self.current_year}

Total Deployments: {stats['total_deployments']}
Successful Builds: {stats['successful_builds']}
Failed Builds: {stats['failed_builds']}
Build Success Rate: {stats.get('build_success_rate', 0):.1f}%

Successful Deploys: {stats['successful_deploys']}
Failed Deploys: {stats['failed_deploys']}
Deploy Success Rate: {stats.get('deploy_success_rate', 0):.1f}%

Active Projects: {project_count}
"""
        self.stats_text.setPlainText(stats_text)
        
    def update_deployments_table(self):
        """Update deployments table"""
        all_deployments = []
        
        # Flatten all deployments from all projects
        for project_name, deployments in self.current_data.items():
            all_deployments.extend(deployments)
            
        # Sort by timestamp (newest first)
        all_deployments.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Update table
        self.deployments_table.setRowCount(len(all_deployments))
        
        for row, deployment in enumerate(all_deployments):
            items = [
                deployment.get('jira_patch_id', 'N/A'),
                deployment.get('timestamp', ''),
                deployment.get('project_name', ''),
                deployment.get('component_name', ''),
                deployment.get('environment', ''),
                deployment.get('developer_name', ''),
                'Success' if deployment.get('build_status') else 'Failed',
                'Success' if deployment.get('deploy_status') else 'Failed',
                deployment.get('notes', '')
            ]
            
            for col, item_text in enumerate(items):
                item = QTableWidgetItem(str(item_text))
                
                # Color code status columns
                if col == 6:  # Build Status
                    if item_text == 'Success':
                        item.setBackground(QColor("#d4edda"))
                        item.setForeground(QColor("#155724"))
                    else:
                        item.setBackground(QColor("#f8d7da"))
                        item.setForeground(QColor("#721c24"))
                        
                if col == 7:  # Deploy Status
                    if item_text == 'Success':
                        item.setBackground(QColor("#d4edda"))
                        item.setForeground(QColor("#155724"))
                    else:
                        item.setBackground(QColor("#f8d7da"))
                        item.setForeground(QColor("#721c24"))
                        
                self.deployments_table.setItem(row, col, item)
                
    def update_statistics(self):
        """Update statistics tabs"""
        stats = self.excel_manager.get_deployment_stats(self.current_month, self.current_year)
        
        # Component stats
        component_counts = stats.get('component_counts', {})
        component_text = "Component Deployment Counts:\n\n"
        for component, count in component_counts.items():
            component_text += f"{component:.<20} {count:>5}\n"
        self.component_stats.setPlainText(component_text)
        
        # Project stats
        project_counts = stats.get('project_counts', {})
        project_text = "Project Deployment Counts:\n\n"
        for project, count in sorted(project_counts.items()):
            project_text += f"{project:.<25} {count:>5}\n"
        self.project_stats.setPlainText(project_text)
        
        # Success analysis
        success_text = f"""Success Rate Analysis:

Build Success Rate: {stats.get('build_success_rate', 0):.1f}%
  ✓ Successful: {stats.get('successful_builds', 0)}
  ✗ Failed: {stats.get('failed_builds', 0)}

Deploy Success Rate: {stats.get('deploy_success_rate', 0):.1f}%
  ✓ Successful: {stats.get('successful_deploys', 0)}
  ✗ Failed: {stats.get('failed_deploys', 0)}
"""
        self.success_stats.setPlainText(success_text)
        
    def update_project_filter(self):
        """Update project filter dropdown"""
        current_selection = self.project_filter.currentText()
        self.project_filter.clear()
        self.project_filter.addItem("All Projects")
        
        project_names = list(self.current_data.keys())
        project_names.sort()
        
        for project_name in project_names:
            self.project_filter.addItem(project_name)
            
        # Restore selection if possible
        index = self.project_filter.findText(current_selection)
        if index >= 0:
            self.project_filter.setCurrentIndex(index)
            
    def filter_deployments(self, project_filter):
        """Filter deployments table by project"""
        if project_filter == "All Projects":
            self.update_deployments_table()
            return
            
        # Filter deployments
        filtered_deployments = []
        if project_filter in self.current_data:
            filtered_deployments = self.current_data[project_filter]
            
        # Sort by timestamp
        filtered_deployments.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Update table with filtered data
        self.deployments_table.setRowCount(len(filtered_deployments))
        
        for row, deployment in enumerate(filtered_deployments):
            items = [
                deployment.get('jira_patch_id', 'N/A'),
                deployment.get('timestamp', ''),
                deployment.get('project_name', ''),
                deployment.get('component_name', ''),
                deployment.get('environment', ''),
                deployment.get('developer_name', ''),
                'Success' if deployment.get('build_status') else 'Failed',
                'Success' if deployment.get('deploy_status') else 'Failed',
                deployment.get('notes', '')
            ]
            
            for col, item_text in enumerate(items):
                item = QTableWidgetItem(str(item_text))
                
                # Color code status columns
                if col == 6 or col == 7:  # Status columns
                    if item_text == 'Success':
                        item.setBackground(QColor("#d4edda"))
                        item.setForeground(QColor("#155724"))
                    else:
                        item.setBackground(QColor("#f8d7da"))
                        item.setForeground(QColor("#721c24"))
                        
                self.deployments_table.setItem(row, col, item)
                
    def export_excel(self):
        """Export current month's data to combined Excel"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            month_name = calendar.month_name[self.current_month]
            default_name = f"Deployments_{month_name}_{self.current_year}.xlsx"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel Report", default_name, "Excel Files (*.xlsx)"
            )
            
            if file_path:
                # Create combined Excel file
                self.create_combined_excel(file_path)
                QMessageBox.information(self, "Success", f"Excel report exported to:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export Excel: {str(e)}")
            
    def create_combined_excel(self, output_path):
        """Create combined Excel file with all projects"""
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        wb = Workbook()
        ws = wb.active
        ws.title = f"{calendar.month_name[self.current_month]}_{self.current_year}"
        
        # Headers
        headers = [
            "JIRA PATCH ID", "Timestamp", "Project Name", "Component Name", 
            "Environment", "SVN/GIT URL", "Developer Name", "Build Server",
            "Deploy Server", "Database Name", "Database Script", "Backup Location",
            "Build Status", "Deploy Status", "Notes", "Deployed By"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
            
        # Data
        row = 2
        for project_name, deployments in self.current_data.items():
            for deployment in deployments:
                ws.cell(row=row, column=1, value=deployment.get('jira_patch_id', 'N/A'))
                ws.cell(row=row, column=2, value=deployment.get('timestamp', ''))
                ws.cell(row=row, column=3, value=deployment.get('project_name', ''))
                ws.cell(row=row, column=4, value=deployment.get('component_name', ''))
                ws.cell(row=row, column=5, value=deployment.get('environment', ''))
                ws.cell(row=row, column=6, value=deployment.get('vcs_url', ''))
                ws.cell(row=row, column=7, value=deployment.get('developer_name', ''))
                ws.cell(row=row, column=8, value=deployment.get('build_server', ''))
                ws.cell(row=row, column=9, value=deployment.get('deploy_server', ''))
                ws.cell(row=row, column=10, value=deployment.get('database_name', ''))
                ws.cell(row=row, column=11, value=deployment.get('database_script', 'N/A'))
                ws.cell(row=row, column=12, value=deployment.get('backup_location', ''))
                ws.cell(row=row, column=13, value='Success' if deployment.get('build_status') else 'Failed')
                ws.cell(row=row, column=14, value='Success' if deployment.get('deploy_status') else 'Failed')
                ws.cell(row=row, column=15, value=deployment.get('notes', ''))
                ws.cell(row=row, column=16, value=deployment.get('deployed_by', ''))
                row += 1
                
        # Auto-adjust column widths
        for col in range(1, len(headers) + 1):
            ws.column_dimensions[chr(64 + col)].width = 15
            
        wb.save(output_path)
        
    def generate_pdf(self):
        """Generate PDF report"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.pdf_btn.setEnabled(False)
            
            # Start PDF generation in thread
            self.pdf_thread = PDFGenerationThread(
                self.current_month, self.current_year, self.excel_manager
            )
            self.pdf_thread.progress.connect(self.progress_bar.setValue)
            self.pdf_thread.finished.connect(self.on_pdf_finished)
            self.pdf_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate PDF: {str(e)}")
            self.progress_bar.setVisible(False)
            self.pdf_btn.setEnabled(True)
            
    def on_pdf_finished(self, success, result):
        """Handle PDF generation completion"""
        self.progress_bar.setVisible(False)
        self.pdf_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", f"PDF report generated:\n{result}")
        else:
            QMessageBox.critical(self, "Error", f"PDF generation failed:\n{result}")


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = SimpleReportsViewer()
    window.show()
    sys.exit(app.exec_())