#!/usr/bin/env python3
"""
Simple Deployment Checklist Tool - New Excel-Based Version
Main Entry Point
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter

from ui.dark_theme import get_dark_theme
from ui.simple_deployment_new import SimpleDeploymentForm
from ui.simple_projects_form import SimpleProjectsTab
from ui.simple_reports import SimpleReportsViewer
from ui.simple_last_saved import LastSavedTab
from ui.simple_settings import SimpleSettingsTab
from ui.simple_about import SimpleAboutTab


class SimpleMainWindow(QMainWindow):
    """Simple main window with Excel-based deployment tracking"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize simple UI"""
        self.setWindowTitle("📋 chklst - Excel-Based Deployment Tracker")
        
        # Create clipboard icon
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw clipboard background (green)
        painter.setBrush(Qt.green)
        painter.setPen(Qt.darkGreen)
        painter.drawRoundedRect(6, 4, 20, 26, 2, 2)
        
        # Draw clipboard clip (darker green)
        painter.setBrush(Qt.darkGreen)
        painter.drawRoundedRect(12, 2, 8, 6, 1, 1)
        
        # Draw checkmarks (white)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 8, QFont.Bold))
        painter.drawText(10, 16, "✓")
        painter.drawText(10, 22, "✓")
        painter.drawText(10, 28, "✓")
        
        painter.end()
        
        self.setWindowIcon(QIcon(pixmap))
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply dark theme
        self.setStyleSheet(get_dark_theme())
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add tabs
        self.deployment_tab = SimpleDeploymentForm()
        self.projects_tab = SimpleProjectsTab()
        self.last_saved_tab = LastSavedTab()
        self.reports_tab = SimpleReportsViewer()
        self.settings_tab = SimpleSettingsTab()
        self.about_tab = SimpleAboutTab()

        self.tab_widget.addTab(self.deployment_tab, "📝 Deployment")
        self.tab_widget.addTab(self.projects_tab, "📁 Projects")
        self.tab_widget.addTab(self.last_saved_tab, "💾 Last Saved")
        self.tab_widget.addTab(self.reports_tab, "📊 Reports")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        self.tab_widget.addTab(self.about_tab, "ℹ️ About")
        
        # Connect signals for refresh
        self.projects_tab.projects_updated.connect(self.refresh_deployment_projects)
        
    def refresh_deployment_projects(self):
        """Refresh project list in deployment tab"""
        self.deployment_tab.load_projects()
        

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Create application icon
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw clipboard background (green)
    painter.setBrush(Qt.green)
    painter.setPen(Qt.darkGreen)
    painter.drawRoundedRect(6, 4, 20, 26, 2, 2)
    
    # Draw clipboard clip (darker green)
    painter.setBrush(Qt.darkGreen)
    painter.drawRoundedRect(12, 2, 8, 6, 1, 1)
    
    # Draw checkmarks (white)
    painter.setPen(Qt.white)
    painter.setFont(QFont("Arial", 8, QFont.Bold))
    painter.drawText(10, 16, "✓")
    painter.drawText(10, 22, "✓")
    painter.drawText(10, 28, "✓")
    
    painter.end()
    
    # Set application icon
    app.setWindowIcon(QIcon(pixmap))
    
    window = SimpleMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()