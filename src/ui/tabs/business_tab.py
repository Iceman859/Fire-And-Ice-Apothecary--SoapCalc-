"""UI Business Tab - Profit Analysis and Pricing"""

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QInputDialog,
)


class ProfitAnalysisWidget(QWidget):
    """Widget for calculating business profit and pricing"""

    def __init__(self):
        super().__init__()
        self.batch_cost = 0.0
        self.bar_count = 0.0
        self.settings = QSettings("FireAndIceApothecary", "SoapCalc")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Presets Group
        preset_group = QGroupBox("Presets")
        p_layout = QHBoxLayout()
        p_layout.addWidget(QLabel("Load Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Select Preset...")
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
        p_layout.addWidget(self.preset_combo)

        save_btn = QPushButton("Save Current")
        save_btn.clicked.connect(self.save_preset)
        p_layout.addWidget(save_btn)

        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(self.delete_preset)
        p_layout.addWidget(del_btn)
        preset_group.setLayout(p_layout)
        layout.addWidget(preset_group)

        # Inputs
        input_group = QGroupBox("Cost & Pricing Inputs")
        form = QFormLayout()

        self.labor_rate_spin = QDoubleSpinBox()
        self.labor_rate_spin.setRange(0, 500)
        self.labor_rate_spin.setValue(20.0)  # $20/hr default
        self.labor_rate_spin.setKeyboardTracking(False)
        self.labor_rate_spin.valueChanged.connect(self.calculate_profit)
        form.addRow("Labor Rate ($/hr):", self.labor_rate_spin)

        self.labor_hours_spin = QDoubleSpinBox()
        self.labor_hours_spin.setRange(0, 100)
        self.labor_hours_spin.setValue(1.0)
        self.labor_hours_spin.setSingleStep(0.25)
        self.labor_hours_spin.setKeyboardTracking(False)
        self.labor_hours_spin.valueChanged.connect(self.calculate_profit)
        form.addRow("Labor Hours (Batch):", self.labor_hours_spin)

        self.waste_spin = QDoubleSpinBox()
        self.waste_spin.setRange(0, 100)
        self.waste_spin.setValue(5.0)  # Default 5% waste
        self.waste_spin.setSuffix("%")
        self.waste_spin.setToolTip(
            "Buffer for batter left in bowl, spills, or cure shrinkage"
        )
        self.waste_spin.valueChanged.connect(self.calculate_profit)
        form.addRow("Waste / Shrinkage:", self.waste_spin)

        self.packaging_cost_spin = QDoubleSpinBox()
        self.packaging_cost_spin.setRange(0, 50)
        self.packaging_cost_spin.setValue(0.50)
        self.packaging_cost_spin.setKeyboardTracking(False)
        self.packaging_cost_spin.valueChanged.connect(self.calculate_profit)
        form.addRow("Packaging Cost ($/unit):", self.packaging_cost_spin)

        self.overhead_spin = QDoubleSpinBox()
        self.overhead_spin.setRange(0, 100)
        self.overhead_spin.setValue(10.0)
        self.overhead_spin.setToolTip(
            "Percentage of material + labor to cover overhead (electricity, rent, etc)"
        )
        self.overhead_spin.setKeyboardTracking(False)
        self.overhead_spin.valueChanged.connect(self.calculate_profit)
        form.addRow("Overhead Markup (%):", self.overhead_spin)

        self.profit_margin_spin = QDoubleSpinBox()
        self.profit_margin_spin.setRange(0, 500)
        self.profit_margin_spin.setValue(50.0)
        self.profit_margin_spin.setKeyboardTracking(False)
        self.profit_margin_spin.valueChanged.connect(self.calculate_profit)
        form.addRow("Desired Profit Margin (%):", self.profit_margin_spin)

        input_group.setLayout(form)
        layout.addWidget(input_group)

        # Results
        results_group = QGroupBox("Financial Analysis")
        r_layout = QFormLayout()

        self.total_cogs_lbl = QLabel("$0.00")
        r_layout.addRow("Total Batch Cost (Mat + Labor + Ovhd):", self.total_cogs_lbl)

        self.cogs_per_bar_lbl = QLabel("$0.00")
        self.cogs_per_bar_lbl.setStyleSheet("font-weight: bold;")
        r_layout.addRow("Cost Per Bar (Production):", self.cogs_per_bar_lbl)

        self.wholesale_price_lbl = QLabel("$0.00")
        r_layout.addRow("Suggested Wholesale Price:", self.wholesale_price_lbl)

        self.retail_price_lbl = QLabel("$0.00")
        self.retail_price_lbl.setStyleSheet(
            "font-weight: bold; color: #4fc3f7; font-size: 14px;"
        )
        r_layout.addRow("Suggested Retail Price:", self.retail_price_lbl)

        self.profit_per_batch_lbl = QLabel("$0.00")
        r_layout.addRow("Net Profit Per Batch:", self.profit_per_batch_lbl)

        results_group.setLayout(r_layout)
        layout.addWidget(results_group)

        layout.addStretch()
        self.setLayout(layout)

        self.load_presets()

    def update_data(self, batch_material_cost, bar_count):
        self.batch_cost = batch_material_cost
        self.bar_count = bar_count
        self.calculate_profit()

    def calculate_profit(self):
        labor_cost = self.labor_rate_spin.value() * self.labor_hours_spin.value()
        overhead_pct = self.overhead_spin.value() / 100.0
        waste_pct = self.waste_spin.value() / 100.0

        # Apply waste factor to material cost (you pay for ingredients you don't sell)
        adjusted_material_cost = self.batch_cost * (1 + waste_pct)
        base_cost = adjusted_material_cost + labor_cost
        total_batch_cost = base_cost * (1 + overhead_pct)

        packaging_total = self.packaging_cost_spin.value() * self.bar_count
        total_cogs = total_batch_cost + packaging_total

        cogs_per_bar = total_cogs / self.bar_count if self.bar_count > 0 else 0.0

        margin_pct = self.profit_margin_spin.value() / 100.0
        # Simple markup model: Cost * (1 + Margin)
        retail_price = cogs_per_bar * (1 + margin_pct)
        wholesale_price = retail_price * 0.5  # Rule of thumb: Wholesale is half retail

        profit_per_batch = (retail_price * self.bar_count) - total_cogs

        self.total_cogs_lbl.setText(f"${total_cogs:.2f}")
        self.cogs_per_bar_lbl.setText(f"${cogs_per_bar:.2f}")
        self.wholesale_price_lbl.setText(f"${wholesale_price:.2f}")
        self.retail_price_lbl.setText(f"${retail_price:.2f}")
        self.profit_per_batch_lbl.setText(f"${profit_per_batch:.2f}")

    def set_packaging_cost(self, cost: float):
        """Public method to sync packaging cost from another widget."""
        self.packaging_cost_spin.blockSignals(True)
        self.packaging_cost_spin.setValue(cost)
        self.packaging_cost_spin.blockSignals(False)
        self.calculate_profit()

    def load_presets(self):
        """Load presets from settings"""
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem("Select Preset...")

        presets = self.settings.value("profit_presets", {})
        if presets:
            self.preset_combo.addItems(sorted(presets.keys()))
        self.preset_combo.blockSignals(False)

    def save_preset(self):
        """Save current values as a new preset"""
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset Name:")
        if ok and name:
            presets = self.settings.value("profit_presets", {})
            presets[name] = {
                "labor_rate": self.labor_rate_spin.value(),
                "labor_hours": self.labor_hours_spin.value(),
                "waste": self.waste_spin.value(),
                "packaging": self.packaging_cost_spin.value(),
                "overhead": self.overhead_spin.value(),
                "margin": self.profit_margin_spin.value(),
            }
            self.settings.setValue("profit_presets", presets)
            self.load_presets()
            self.preset_combo.setCurrentText(name)

    def delete_preset(self):
        """Delete selected preset"""
        name = self.preset_combo.currentText()
        if name == "Select Preset...":
            return

        presets = self.settings.value("profit_presets", {})
        if name in presets:
            del presets[name]
            self.settings.setValue("profit_presets", presets)
            self.load_presets()

    def apply_preset(self, name):
        """Apply selected preset values"""
        if name == "Select Preset...":
            return

        presets = self.settings.value("profit_presets", {})
        data = presets.get(name)
        if data:
            self.labor_rate_spin.setValue(float(data.get("labor_rate", 20.0)))
            self.labor_hours_spin.setValue(float(data.get("labor_hours", 1.0)))
            self.waste_spin.setValue(float(data.get("waste", 5.0)))
            self.packaging_cost_spin.setValue(float(data.get("packaging", 0.50)))
            self.overhead_spin.setValue(float(data.get("overhead", 10.0)))
            self.profit_margin_spin.setValue(float(data.get("margin", 50.0)))
