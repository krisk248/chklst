"""
Simple dark theme for deployment checklist tool
"""

def get_dark_theme():
    """Simple dark theme stylesheet"""
    return """
    QMainWindow, QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: Arial, sans-serif;
        font-size: 12px;
    }
    
    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #2b2b2b;
    }
    
    QTabBar::tab {
        background-color: #404040;
        color: #ffffff;
        padding: 8px 16px;
        margin-right: 2px;
        border: 1px solid #555555;
    }
    
    QTabBar::tab:selected {
        background-color: #4a9eff;
        color: #ffffff;
    }
    
    QTabBar::tab:hover {
        background-color: #505050;
    }
    
    QLabel {
        color: #ffffff;
        background-color: transparent;
    }
    
    QComboBox {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 5px;
        min-height: 25px;
    }
    
    QComboBox:hover {
        border-color: #4a9eff;
    }
    
    QComboBox::drop-down {
        border: none;
        background-color: #555555;
        width: 20px;
    }
    
    QComboBox QAbstractItemView {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        selection-background-color: #4a9eff;
    }
    
    QLineEdit {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 5px;
        min-height: 25px;
    }
    
    QLineEdit:focus {
        border-color: #4a9eff;
    }
    
    QTextEdit {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 5px;
    }
    
    QTextEdit:focus {
        border-color: #4a9eff;
    }
    
    QCheckBox {
        color: #ffffff;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #555555;
        background-color: #404040;
    }
    
    QCheckBox::indicator:checked {
        background-color: #4caf50;
        border-color: #4caf50;
    }
    
    QCheckBox::indicator:hover {
        border-color: #4a9eff;
    }
    
    QPushButton {
        background-color: #4a9eff;
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        min-height: 30px;
    }
    
    QPushButton:hover {
        background-color: #357abd;
    }
    
    QPushButton:pressed {
        background-color: #2563a8;
    }
    
    QGroupBox {
        border: 1px solid #555555;
        margin-top: 10px;
        padding-top: 10px;
        color: #ffffff;
    }
    
    QGroupBox::title {
        color: #4a9eff;
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 10px 0 10px;
    }
    
    QTableWidget {
        background-color: #404040;
        color: #ffffff;
        border: 1px solid #555555;
        gridline-color: #555555;
        selection-background-color: #4a9eff;
    }
    
    QHeaderView::section {
        background-color: #505050;
        color: #ffffff;
        padding: 5px;
        border: 1px solid #555555;
    }
    
    QScrollBar:vertical {
        background-color: #404040;
        width: 12px;
        border: none;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        min-height: 20px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #666666;
    }
    """