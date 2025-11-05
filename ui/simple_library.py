"""
Library/Presets Tab - Manage reusable data
Clean interface for managing developers, servers, environments
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QListWidget, QPushButton, QInputDialog, QMessageBox,
    QLabel, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from utils.library_manager import LibraryManager


class SimpleLibraryTab(QWidget):
    """Simple library/presets management tab"""

    library_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.library_manager = LibraryManager()
        self.init_ui()
        self.load_all_data()

    def init_ui(self):
        """Initialize UI"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        # Main widget inside scroll area
        main_widget = QWidget()
        scroll.setWidget(main_widget)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(scroll)

        # Content layout
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("📚 LIBRARY / PRESETS")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #4a9eff; margin-bottom: 10px;")
        layout.addWidget(header)

        info = QLabel("Manage reusable data for dropdowns across the application")
        info.setStyleSheet("color: #7f8c8d; font-style: italic; margin-bottom: 20px;")
        layout.addWidget(info)

        # Create library sections
        self.create_developers_section(layout)
        self.create_build_servers_section(layout)
        self.create_deploy_servers_section(layout)
        self.create_environments_section(layout)

        layout.addStretch()

    def create_developers_section(self, parent_layout):
        """Create developers management section"""
        group = QGroupBox("👥 DEVELOPERS")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        layout = QVBoxLayout(group)

        # List widget
        self.developers_list = QListWidget()
        self.developers_list.setMaximumHeight(150)
        layout.addWidget(self.developers_list)

        # Buttons
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("+ Add Developer")
        add_btn.clicked.connect(self.add_developer)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("× Remove Selected")
        remove_btn.clicked.connect(self.remove_developer)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        parent_layout.addWidget(group)

    def create_build_servers_section(self, parent_layout):
        """Create build servers management section"""
        group = QGroupBox("🖥️ BUILD SERVERS")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        layout = QVBoxLayout(group)

        # List widget
        self.build_servers_list = QListWidget()
        self.build_servers_list.setMaximumHeight(150)
        layout.addWidget(self.build_servers_list)

        # Buttons
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("+ Add Server")
        add_btn.clicked.connect(self.add_build_server)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("× Remove Selected")
        remove_btn.clicked.connect(self.remove_build_server)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        parent_layout.addWidget(group)

    def create_deploy_servers_section(self, parent_layout):
        """Create deploy servers management section"""
        group = QGroupBox("🌐 DEPLOY SERVERS")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        layout = QVBoxLayout(group)

        # List widget
        self.deploy_servers_list = QListWidget()
        self.deploy_servers_list.setMaximumHeight(150)
        layout.addWidget(self.deploy_servers_list)

        # Buttons
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("+ Add Server")
        add_btn.clicked.connect(self.add_deploy_server)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("× Remove Selected")
        remove_btn.clicked.connect(self.remove_deploy_server)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        parent_layout.addWidget(group)

    def create_environments_section(self, parent_layout):
        """Create environments management section"""
        group = QGroupBox("🏷️ ENVIRONMENTS")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        layout = QVBoxLayout(group)

        # List widget
        self.environments_list = QListWidget()
        self.environments_list.setMaximumHeight(150)
        layout.addWidget(self.environments_list)

        # Buttons
        btn_layout = QHBoxLayout()

        add_btn = QPushButton("+ Add Environment")
        add_btn.clicked.connect(self.add_environment)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("× Remove Selected")
        remove_btn.clicked.connect(self.remove_environment)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        parent_layout.addWidget(group)

    def load_all_data(self):
        """Load all library data into lists"""
        self.load_developers()
        self.load_build_servers()
        self.load_deploy_servers()
        self.load_environments()

    def load_developers(self):
        """Load developers into list"""
        self.developers_list.clear()
        developers = self.library_manager.get_developers()
        self.developers_list.addItems(developers)

    def load_build_servers(self):
        """Load build servers into list"""
        self.build_servers_list.clear()
        servers = self.library_manager.get_build_servers()
        self.build_servers_list.addItems(servers)

    def load_deploy_servers(self):
        """Load deploy servers into list"""
        self.deploy_servers_list.clear()
        servers = self.library_manager.get_deploy_servers()
        self.deploy_servers_list.addItems(servers)

    def load_environments(self):
        """Load environments into list"""
        self.environments_list.clear()
        environments = self.library_manager.get_environments()
        self.environments_list.addItems(environments)

    # Developer operations
    def add_developer(self):
        """Add a new developer"""
        name, ok = QInputDialog.getText(
            self,
            "Add Developer",
            "Enter developer name:"
        )

        if ok and name:
            if self.library_manager.add_developer(name):
                self.load_developers()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Developer '{name}' added successfully!")
            else:
                QMessageBox.warning(self, "Duplicate", f"Developer '{name}' already exists!")

    def remove_developer(self):
        """Remove selected developer"""
        current_item = self.developers_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a developer to remove!")
            return

        name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove developer '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.library_manager.remove_developer(name):
                self.load_developers()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Developer '{name}' removed successfully!")

    # Build Server operations
    def add_build_server(self):
        """Add a new build server"""
        server, ok = QInputDialog.getText(
            self,
            "Add Build Server",
            "Enter build server address:"
        )

        if ok and server:
            if self.library_manager.add_build_server(server):
                self.load_build_servers()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Build server '{server}' added successfully!")
            else:
                QMessageBox.warning(self, "Duplicate", f"Build server '{server}' already exists!")

    def remove_build_server(self):
        """Remove selected build server"""
        current_item = self.build_servers_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a build server to remove!")
            return

        server = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove build server '{server}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.library_manager.remove_build_server(server):
                self.load_build_servers()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Build server '{server}' removed successfully!")

    # Deploy Server operations
    def add_deploy_server(self):
        """Add a new deploy server"""
        server, ok = QInputDialog.getText(
            self,
            "Add Deploy Server",
            "Enter deploy server address:"
        )

        if ok and server:
            if self.library_manager.add_deploy_server(server):
                self.load_deploy_servers()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Deploy server '{server}' added successfully!")
            else:
                QMessageBox.warning(self, "Duplicate", f"Deploy server '{server}' already exists!")

    def remove_deploy_server(self):
        """Remove selected deploy server"""
        current_item = self.deploy_servers_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a deploy server to remove!")
            return

        server = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove deploy server '{server}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.library_manager.remove_deploy_server(server):
                self.load_deploy_servers()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Deploy server '{server}' removed successfully!")

    # Environment operations
    def add_environment(self):
        """Add a new environment"""
        env, ok = QInputDialog.getText(
            self,
            "Add Environment",
            "Enter environment name:"
        )

        if ok and env:
            if self.library_manager.add_environment(env):
                self.load_environments()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Environment '{env}' added successfully!")
            else:
                QMessageBox.warning(self, "Duplicate", f"Environment '{env}' already exists!")

    def remove_environment(self):
        """Remove selected environment"""
        current_item = self.environments_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select an environment to remove!")
            return

        env = current_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove environment '{env}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.library_manager.remove_environment(env):
                self.load_environments()
                self.library_updated.emit()
                QMessageBox.information(self, "Success", f"Environment '{env}' removed successfully!")
