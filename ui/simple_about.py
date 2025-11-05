"""
About Tab for chklst Application
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

class SimpleAboutTab(QWidget):
    """About tab showing app information"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize About UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # App Logo/Title Section
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # App Title
        title_label = QLabel("chklst")
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #4A90E2; margin: 10px;")
        title_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Deployment Management Tool")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #7F8C8D; margin-bottom: 20px;")
        title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        
        # App Information
        info_group = QGroupBox("Application Information")
        info_layout = QVBoxLayout(info_group)
        
        app_info = QTextEdit()
        app_info.setReadOnly(True)
        app_info.setMaximumHeight(200)
        app_info.setHtml("""
        <h3>chklst v1.0.0</h3>
        <p><strong>Description:</strong> A comprehensive deployment management tool for tracking software deployments, managing project components, and generating deployment reports.</p>
        
        <p><strong>Features:</strong></p>
        <ul>
            <li>Multi-component deployment tracking</li>
            <li>Developer assignment per component</li>
            <li>Excel export with professional formatting</li>
            <li>JIRA and Teams integration formats</li>
            <li>Deployment history and analytics</li>
        </ul>
        """)
        info_layout.addWidget(app_info)
        layout.addWidget(info_group)
        
        # Company & Developer Information
        dev_group = QGroupBox("Development Information")
        dev_layout = QVBoxLayout(dev_group)
        
        dev_info = QTextEdit()
        dev_info.setReadOnly(True)
        dev_info.setMaximumHeight(120)
        dev_info.setHtml("""
        <p><strong>Developed for:</strong> TTS (Technology & Transformation Services)</p>
        <p><strong>Developer:</strong> Kannan</p>
        <p><strong>Version:</strong> 1.0.0</p>
        <p><strong>Built with:</strong> Python, PyQt5, SQLAlchemy</p>
        """)
        dev_layout.addWidget(dev_info)
        layout.addWidget(dev_group)
        
        # Technical Details
        tech_group = QGroupBox("Technical Information")
        tech_layout = QVBoxLayout(tech_group)
        
        tech_info = QTextEdit()
        tech_info.setReadOnly(True)
        tech_info.setMaximumHeight(100)
        tech_info.setHtml("""
        <p><strong>Database:</strong> SQLite</p>
        <p><strong>Export Formats:</strong> Excel (XLSX), JIRA, Microsoft Teams</p>
        <p><strong>Platform:</strong> Cross-platform (Windows, macOS, Linux)</p>
        """)
        tech_layout.addWidget(tech_info)
        layout.addWidget(tech_group)
        
        layout.addStretch()
        
        # Footer
        footer_label = QLabel("© 2025 TTS - Technology & Transformation Services")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #7F8C8D; font-size: 10px; margin-top: 20px;")
        layout.addWidget(footer_label)