"""
Application Launcher / Splash Screen
Allows selection between different calculator modules.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QSpacerItem, QSizePolicy, QDialog, QComboBox, QFormLayout
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fire & Ice Apothecary")
        self.setFixedSize(500, 450)
        self.settings = QSettings("FireAndIceApothecary", "SoapCalc")
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Fire & Ice Apothecary")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        subtitle = QLabel("Select a Module")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_font = QFont()
        sub_font.setPointSize(12)
        subtitle.setFont(sub_font)
        subtitle.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Buttons
        self.btn_soap = self.create_button("Soap Making", "Lye, Oils, and Batch Costing")
        self.btn_soap.clicked.connect(self.launch_soap)
        layout.addWidget(self.btn_soap)
        
        self.btn_infusion = self.create_button("Infusions", "Coming Soon")
        self.btn_infusion.setEnabled(False)
        layout.addWidget(self.btn_infusion)
        
        # Settings Button
        self.btn_settings = QPushButton("Settings / Theme")
        self.btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(self.btn_settings)
        
        layout.addStretch()
        self.setLayout(layout)

    def create_button(self, text, subtext):
        btn = QPushButton()
        btn.setText(f"{text}\n{subtext}")
        btn.setMinimumHeight(80)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def apply_theme(self):
        # Load theme from settings
        theme_name = self.settings.value("theme_accent", "Blue")
        themes = {
            "Blue": {"accent": "#0d47a1", "hover": "#1565c0", "pressed": "#0a3d91"},
            "Green": {"accent": "#2e7d32", "hover": "#388e3c", "pressed": "#1b5e20"},
            "Red": {"accent": "#c62828", "hover": "#d32f2f", "pressed": "#b71c1c"},
            "Purple": {"accent": "#6a1b9a", "hover": "#7b1fa2", "pressed": "#4a148c"},
            "Orange": {"accent": "#ef6c00", "hover": "#f57c00", "pressed": "#e65100"},
            "Teal": {"accent": "#00695c", "hover": "#00796b", "pressed": "#004d40"},
        }
        colors = themes.get(theme_name, themes["Blue"])
        accent = colors["accent"]
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #1e1e1e;
                color: #e0e0e0;
            }}
            QPushButton {{
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background-color: #3d3d3d;
                border: 1px solid {accent};
            }}
            QPushButton:pressed {{
                background-color: {accent};
            }}
            QPushButton:disabled {{
                background-color: #252525;
                color: #555555;
                border: 1px solid #2d2d2d;
            }}
        """)

    def launch_soap(self):
        # Import locally to avoid circular imports or heavy load at startup
        from src.ui.main_window import MainWindow
        self.soap_window = MainWindow()
        self.soap_window.show()
        self.close()

    def open_settings(self):
        """Open simple settings dialog for theme"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.setFixedSize(300, 150)
        
        layout = QFormLayout()
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Blue", "Green", "Red", "Purple", "Orange", "Teal"])
        current_theme = self.settings.value("theme_accent", "Blue")
        theme_combo.setCurrentText(current_theme)
        
        layout.addRow("Theme Accent:", theme_combo)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: [self.settings.setValue("theme_accent", theme_combo.currentText()), self.apply_theme(), dialog.accept()])
        layout.addRow(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec()