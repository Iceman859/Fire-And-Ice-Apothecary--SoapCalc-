"""Mold Volume Tab"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, QSettings, Qt
import math
from PyQt6.QtWidgets import (
    QFormLayout,
    QMessageBox,
    QInputDialog,
    QStackedWidget,
    QRadioButton,
    QCheckBox,
    QSpinBox,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QDoubleSpinBox,
)
from src.models import SoapCalculator
from src.utils.helpers import SelectAllSpinBox


class MoldVolumeWidget(QWidget):
    """Widget to calculate mold volume and required batch size"""

    weight_calculated = pyqtSignal(float)

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.settings = QSettings("FireAndIceApothecary", "SoapCalc")
        self.presets = [
            ('10" Loaf (Standard)', 87.5, "10 x 3.5 x 2.5 inches"),
            ("Tall Skinny Loaf", 87.5, "10 x 2.5 x 3.5 inches"),
            ("12 Bar Slab", 160.0, "8 x 8 x 2.5 inches"),
            ('6" Slab', 45.0, "6 x 6 x 1.25 inches"),
            ("Round Column (PVC)", 60.0, '3" diam x 8.5" tall'),
        ]
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        layout.addWidget(QLabel("<b>Mold Volume Calculator</b>"))
        layout.addWidget(QLabel("Calculate the total oil weight needed for your mold."))

        # Mode Selection
        mode_group = QGroupBox("Mold Type")
        mode_layout = QHBoxLayout()
        self.mode_std = QRadioButton("Standard / Preset")
        self.mode_custom = QRadioButton("Custom Dimensions")
        self.mode_water = QRadioButton("Water Capacity")
        self.mode_std.setChecked(True)

        self.mode_std.toggled.connect(self.toggle_mode)
        self.mode_custom.toggled.connect(self.toggle_mode)
        self.mode_water.toggled.connect(self.toggle_mode)

        mode_layout.addWidget(self.mode_std)
        mode_layout.addWidget(self.mode_custom)
        mode_layout.addWidget(self.mode_water)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Stack for inputs
        self.stack = QStackedWidget()

        # Page 1: Standard Molds
        page_std = QWidget()
        std_layout = QFormLayout()
        self.std_combo = QComboBox()
        self.load_presets()

        std_layout.addRow("Select Mold:", self.std_combo)

        del_preset_btn = QPushButton("Delete Preset")
        del_preset_btn.setToolTip("Delete selected custom preset")
        del_preset_btn.clicked.connect(self.delete_preset)
        std_layout.addRow("", del_preset_btn)

        page_std.setLayout(std_layout)
        self.stack.addWidget(page_std)

        # Page 2: Custom Dimensions
        page_custom = QWidget()
        custom_layout = QFormLayout()

        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Rectangular (Box)", "Cylindrical (Round)"])
        self.shape_combo.currentTextChanged.connect(self.toggle_shape_inputs)
        custom_layout.addRow("Shape:", self.shape_combo)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Inches", "Centimeters"])
        custom_layout.addRow("Dimensions Unit:", self.unit_combo)

        # Box Inputs
        self.box_widget = QWidget()
        box_l = QHBoxLayout(self.box_widget)
        box_l.setContentsMargins(0, 0, 0, 0)
        self.len_spin = SelectAllSpinBox()
        self.len_spin.setRange(0, 100)
        self.wid_spin = SelectAllSpinBox()
        self.wid_spin.setRange(0, 100)
        self.hgt_spin = SelectAllSpinBox()
        self.hgt_spin.setRange(0, 100)
        box_l.addWidget(QLabel("L:"))
        box_l.addWidget(self.len_spin)
        box_l.addWidget(QLabel("W:"))
        box_l.addWidget(self.wid_spin)
        box_l.addWidget(QLabel("H:"))
        box_l.addWidget(self.hgt_spin)
        custom_layout.addRow("Dimensions:", self.box_widget)
        box_lbl = QLabel("Inner Dimensions:")
        box_lbl.setToolTip(
            "Enter the INSIDE dimensions of the mold cavity.\nProduct listings often show external packaging dimensions."
        )
        custom_layout.addRow(box_lbl, self.box_widget)

        # Cylinder Inputs
        self.cyl_widget = QWidget()
        cyl_l = QHBoxLayout(self.cyl_widget)
        cyl_l.setContentsMargins(0, 0, 0, 0)
        self.diam_spin = SelectAllSpinBox()
        self.diam_spin.setRange(0, 100)
        self.cyl_hgt_spin = SelectAllSpinBox()
        self.cyl_hgt_spin.setRange(0, 100)
        cyl_l.addWidget(QLabel("Diameter:"))
        cyl_l.addWidget(self.diam_spin)
        cyl_l.addWidget(QLabel("Height:"))
        cyl_l.addWidget(self.cyl_hgt_spin)
        custom_layout.addRow("Dimensions:", self.cyl_widget)
        cyl_lbl = QLabel("Inner Dimensions:")
        cyl_lbl.setToolTip("Enter the INSIDE dimensions of the mold cavity.")
        custom_layout.addRow(cyl_lbl, self.cyl_widget)
        self.cyl_widget.setVisible(False)

        save_preset_btn = QPushButton("Save as Preset")
        save_preset_btn.clicked.connect(self.save_preset)
        custom_layout.addRow("", save_preset_btn)

        page_custom.setLayout(custom_layout)
        self.stack.addWidget(page_custom)

        # Page 3: Water Capacity
        page_water = QWidget()
        water_layout = QFormLayout()

        self.water_weight_spin = SelectAllSpinBox()
        self.water_weight_spin.setRange(0, 10000)
        self.water_weight_spin.setValue(0)
        self.water_unit_combo = QComboBox()
        self.water_unit_combo.addItems(["oz", "g"])

        w_input = QWidget()
        w_input_l = QHBoxLayout(w_input)
        w_input_l.setContentsMargins(0, 0, 0, 0)
        w_input_l.addWidget(self.water_weight_spin)
        w_input_l.addWidget(self.water_unit_combo)
        water_layout.addRow("Water Weight:", w_input)

        self.water_per_cavity_check = QCheckBox("Weight is per cavity")
        self.water_per_cavity_check.setToolTip(
            "Check this if you weighed one cavity but want to make a batch for the total count below."
        )
        water_layout.addRow("", self.water_per_cavity_check)

        water_layout.addRow(
            QLabel(
                "<small><i>Tip: Place mold on scale, tare, and fill with water to get exact capacity.</i></small>"
            )
        )

        page_water.setLayout(water_layout)
        self.stack.addWidget(page_water)

        layout.addWidget(self.stack)

        # Cavity/Mold Count
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Number of Cavities / Molds:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 100)
        self.count_spin.setValue(1)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        layout.addLayout(count_layout)

        # Calculation Factors
        factors_group = QGroupBox("Calculation Settings")
        f_layout = QFormLayout()

        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0.1, 2.0)
        self.density_spin.setSingleStep(0.01)
        self.density_spin.setValue(0.51)  # Default density for soap batter
        self.density_spin.setToolTip(
            "Density of soap batter.\nWater is ~0.58 oz/in³. Soap is often ~0.60 oz/in³."
        )
        f_layout.addRow("Batter Density (oz/in³):", self.density_spin)

        self.oil_pct_spin = QDoubleSpinBox()
        self.oil_pct_spin.setRange(1, 100)
        self.oil_pct_spin.setValue(70.0)
        self.oil_pct_spin.setSuffix("%")
        self.oil_pct_spin.setToolTip(
            "Percentage of the total batch that is oils.\nTypically 65-70%."
        )
        f_layout.addRow("Oil % of Batch:", self.oil_pct_spin)

        factors_group.setLayout(f_layout)
        layout.addWidget(factors_group)

        # Results
        res_layout = QGridLayout()
        res_layout.addWidget(QLabel("Calculated Volume:"), 0, 0)
        self.vol_lbl = QLabel("0.00")
        res_layout.addWidget(self.vol_lbl, 0, 1)

        res_layout.addWidget(QLabel("Water Capacity (Est):"), 1, 0)
        self.water_capacity_lbl = QLabel("0.00 g")
        self.water_capacity_lbl.setToolTip(
            "Estimated weight if filled with water (Density ~0.578 oz/in³)"
        )
        res_layout.addWidget(self.water_capacity_lbl, 1, 1)

        res_layout.addWidget(QLabel("Total Batter Needed:"), 2, 0)
        self.total_weight_lbl = QLabel("0.00 g")
        self.total_weight_lbl.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #4caf50;"
        )
        res_layout.addWidget(self.total_weight_lbl, 2, 1)

        res_layout.addWidget(QLabel("Required Oil Weight:"), 3, 0)
        self.weight_lbl = QLabel("0.00 g")
        self.weight_lbl.setToolTip(
            "The amount of oils to enter in your recipe to achieve the total batter weight."
        )
        res_layout.addWidget(self.weight_lbl, 3, 1)

        layout.addLayout(res_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        calc_btn = QPushButton("Calculate")
        calc_btn.clicked.connect(self.calculate)
        btn_layout.addWidget(calc_btn)

        apply_btn = QPushButton("Set as Recipe Target")
        apply_btn.clicked.connect(self.apply_target)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()
        self.setLayout(layout)

    def load_presets(self):
        """Load standard and custom presets into combo box"""
        self.std_combo.clear()
        # Standard Presets
        for name, vol, desc in self.presets:
            self.std_combo.addItem(f"{name} ({desc})", vol)

        # Custom Presets from Settings
        customs = self.settings.value("custom_molds", {})
        for name, data in customs.items():
            vol = float(data.get("volume", 0))
            desc = data.get("desc", "")
            self.std_combo.addItem(f"{name} ({desc})", vol)
            # Mark as custom using UserRole
            idx = self.std_combo.count() - 1
            self.std_combo.setItemData(idx, name, Qt.ItemDataRole.UserRole + 1)

    def save_preset(self):
        """Save current custom dimensions as a preset"""
        unit = self.unit_combo.currentText()
        is_inch = unit == "Inches"
        shape = self.shape_combo.currentText()

        vol_raw = 0.0
        desc = ""

        if shape == "Rectangular (Box)":
            l = self.len_spin.value()
            w = self.wid_spin.value()
            h = self.hgt_spin.value()
            vol_raw = l * w * h
            unit_str = "in" if is_inch else "cm"
            desc = f"{l} x {w} x {h} {unit_str}"
        else:
            d = self.diam_spin.value()
            h = self.cyl_hgt_spin.value()
            r = d / 2.0
            vol_raw = math.pi * (r**2) * h
            unit_str = "in" if is_inch else "cm"
            desc = f"{d} diam x {h} {unit_str}"

        if vol_raw <= 0:
            QMessageBox.warning(self, "Error", "Dimensions must be greater than 0.")
            return

        volume_in3 = vol_raw if is_inch else (vol_raw * 0.0610237)

        name, ok = QInputDialog.getText(self, "Save Preset", "Preset Name:")
        if ok and name:
            customs = self.settings.value("custom_molds", {})
            customs[name] = {"volume": volume_in3, "desc": desc}
            self.settings.setValue("custom_molds", customs)
            self.load_presets()

            # Select the new item
            for i in range(self.std_combo.count()):
                key = self.std_combo.itemData(i, Qt.ItemDataRole.UserRole + 1)
                if key == name:
                    self.std_combo.setCurrentIndex(i)
                    break
            QMessageBox.information(self, "Saved", f"Preset '{name}' saved.")

    def delete_preset(self):
        """Delete selected custom preset"""
        idx = self.std_combo.currentIndex()
        if idx < 0:
            return
        key = self.std_combo.itemData(idx, Qt.ItemDataRole.UserRole + 1)
        if not key:
            QMessageBox.information(self, "Info", "Cannot delete standard presets.")
            return
        customs = self.settings.value("custom_molds", {})
        if key in customs:
            del customs[key]
            self.settings.setValue("custom_molds", customs)
            self.load_presets()

    def toggle_mode(self):
        if self.mode_std.isChecked():
            self.stack.setCurrentIndex(0)
        elif self.mode_custom.isChecked():
            self.stack.setCurrentIndex(1)
        else:
            self.stack.setCurrentIndex(2)

    def toggle_shape_inputs(self, text):
        if text == "Rectangular (Box)":
            self.box_widget.setVisible(True)
            self.cyl_widget.setVisible(False)
        else:
            self.box_widget.setVisible(False)
            self.cyl_widget.setVisible(True)

    def calculate(self):
        volume_in3 = 0.0

        if self.mode_std.isChecked():
            # Standard
            volume_in3 = self.std_combo.currentData()
            # Apply Count
            count = self.count_spin.value()
            volume_in3 *= count
        elif self.mode_custom.isChecked():
            # Custom
            unit = self.unit_combo.currentText()
            is_inch = unit == "Inches"

            if self.shape_combo.currentText() == "Rectangular (Box)":
                l = self.len_spin.value()
                w = self.wid_spin.value()
                h = self.hgt_spin.value()
                vol = l * w * h
            else:
                d = self.diam_spin.value()
                h = self.cyl_hgt_spin.value()
                r = d / 2.0
                vol = math.pi * (r**2) * h

            if is_inch:
                volume_in3 = vol
            else:
                # cm3 to in3
                volume_in3 = vol * 0.0610237

            # Apply Count
            count = self.count_spin.value()
            volume_in3 *= count
        else:
            # Water Capacity Mode
            w_val = self.water_weight_spin.value()
            w_unit = self.water_unit_combo.currentText()

            # Convert to grams
            w_grams = w_val * 28.3495 if w_unit == "oz" else w_val

            # Convert water grams to volume (in3)
            # Water density approx 1 g/cm3 = 16.387 g/in3
            volume_in3 = w_grams / 16.387

            if self.water_per_cavity_check.isChecked():
                count = self.count_spin.value()
                volume_in3 *= count

        # Calculate Water Capacity for reference (Density ~0.578 oz/in³)
        water_weight_oz = volume_in3 * 0.578036
        water_weight_g = water_weight_oz * 28.3495
        self.water_capacity_lbl.setText(
            f"{water_weight_g:.1f} g ({water_weight_oz:.2f} oz)"
        )

        # Calculate Total Batter Weight
        # Density is oz batter per cubic inch
        density = self.density_spin.value()
        total_weight_oz = volume_in3 * density
        total_weight_g = total_weight_oz * 28.3495

        # Calculate Oil Weight based on percentage
        oil_pct = self.oil_pct_spin.value() / 100.0
        oil_weight_oz = total_weight_oz * oil_pct
        oil_weight_g = oil_weight_oz * 28.3495

        self.last_calculated_grams = oil_weight_g

        self.vol_lbl.setText(f"{volume_in3:.2f} in³")

        # Display results
        self.total_weight_lbl.setText(
            f"{total_weight_g:.1f} g ({total_weight_oz:.2f} oz)"
        )
        self.weight_lbl.setText(f"{oil_weight_g:.1f} g ({oil_weight_oz:.2f} oz)")

    def apply_target(self):
        self.calculate()
        if hasattr(self, "last_calculated_grams") and self.last_calculated_grams > 0:
            self.weight_calculated.emit(self.last_calculated_grams)
