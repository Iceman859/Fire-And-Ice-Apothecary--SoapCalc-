"""UI SETTINGS TAB"""

from pydoc import text

from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QLineEdit,
)

from src.models import SoapCalculator


class SettingsWidget(QWidget):
    """Widget for recipe settings"""
    unit_text_changed = pyqtSignal(str)
    settings_changed = pyqtSignal()

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        """Setup settings controls"""
        layout = QVBoxLayout()

        # Unit System
        unit_layout = QHBoxLayout()
        unit_layout.addWidget(QLabel("Unit System:"))
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Grams", "Ounces", "Pounds"])
        self.unit_combo.currentTextChanged.connect(self.on_unit_changed)
        unit_layout.addWidget(self.unit_combo)
        layout.addLayout(unit_layout)

        # Theme Accent
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme Accent:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Blue", "Green", "Red", "Purple", "Orange", "Teal"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Company Info
        company_group = QGroupBox("Company Branding (for Reports)")
        c_layout = QFormLayout()
        self.company_name = QLineEdit()
        self.company_name.textChanged.connect(self.save_company_info)
        c_layout.addRow("Company Name:", self.company_name)

        self.website = QLineEdit()
        self.website.textChanged.connect(self.save_company_info)
        c_layout.addRow("Website/Footer:", self.website)
        company_group.setLayout(c_layout)
        layout.addWidget(company_group)

        layout.addStretch()
        self.setLayout(layout)

        # Load settings
        # Block signals to prevent overwriting settings during initialization
        self.company_name.blockSignals(True)
        self.website.blockSignals(True)
        settings = QSettings("FireAndIceApothecary", "SoapCalc")
        self.company_name.setText(str(settings.value("company_name", "")))
        self.website.setText(str(settings.value("company_website", "")))
        self.company_name.blockSignals(False)
        self.website.blockSignals(False)

    def on_unit_changed(self, unit_text: str):
        """Handle unit system change"""
        print(f"DEBUG: RecipeTab received unit change: {unit_text}")
        unit_map = {"Grams": "grams", "Ounces": "ounces", "Pounds": "pounds"}
        new_unit = unit_map.get(unit_text, "grams")
        self.calculator.set_unit_system(new_unit)

        from PyQt6.QtCore import QSettings
        settings = QSettings("FireAndIceApothecary", "SoapCalc")
        settings.setValue("unit_system", unit_text) # Save the Display Name "Ounces"

        math_unit = unit_text.lower() # "grams"
        self.calculator.set_unit_system(math_unit)
        self.settings_changed.emit()
        self.unit_text_changed.emit(unit_text)

    def on_theme_changed(self, theme_text: str):
        """Handle theme accent change"""
        self.settings_changed.emit()

    def save_company_info(self):
        settings = QSettings("FireAndIceApothecary", "SoapCalc")
        settings.setValue("company_name", self.company_name.text())
        settings.setValue("company_website", self.website.text())


    def emit_unit_signal(self, text):
        self.on_unit_changed.emit(text)