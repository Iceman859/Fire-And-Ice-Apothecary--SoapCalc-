"""
Master Batch Management Widget
Allows creation of Oil Blends (saved as custom oils) and Lye Solution calculations.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QHeaderView,
    QMessageBox,
    QFormLayout,
    QSplitter,
)
from PyQt6.QtCore import Qt
from src.data import get_all_oil_names
from src.data.oils import get_oil_info, save_custom_oil, _calc_qualities


class MasterBatchWidget(QWidget):
    def __init__(self, calculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Splitter for two sections
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Left: Oil Blend Creator ---
        oil_widget = QWidget()
        oil_layout = QVBoxLayout(oil_widget)
        oil_layout.setContentsMargins(0, 0, 10, 0)

        oil_layout.addWidget(QLabel("<b>Oil Master Batch (Blend) Creator</b>"))
        oil_layout.addWidget(
            QLabel("Create a pre-mixed blend of oils to use as a single ingredient.")
        )

        # Input
        input_layout = QHBoxLayout()
        self.oil_combo = QComboBox()
        self.oil_combo.setEditable(True)
        self.oil_combo.addItems(get_all_oil_names())
        input_layout.addWidget(self.oil_combo, 2)

        self.percent_spin = QDoubleSpinBox()
        self.percent_spin.setRange(0, 100)
        self.percent_spin.setSuffix("%")
        input_layout.addWidget(self.percent_spin, 1)

        add_btn = QPushButton("Add to Blend")
        add_btn.clicked.connect(self.add_oil_to_blend)
        input_layout.addWidget(add_btn)
        oil_layout.addLayout(input_layout)

        # Table
        self.blend_table = QTableWidget()
        self.blend_table.setColumnCount(2)
        self.blend_table.setHorizontalHeaderLabels(["Oil", "Percentage"])
        self.blend_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        oil_layout.addWidget(self.blend_table)

        # Total & Save
        self.total_lbl = QLabel("Total: 0%")
        oil_layout.addWidget(self.total_lbl)

        save_layout = QHBoxLayout()
        self.blend_name = QComboBox()
        self.blend_name.setEditable(True)
        self.blend_name.setPlaceholderText("Name your blend (e.g. 'Master Batch #1')")
        save_layout.addWidget(self.blend_name)

        save_btn = QPushButton("Save as Custom Oil")
        save_btn.clicked.connect(self.save_blend)
        save_layout.addWidget(save_btn)
        oil_layout.addLayout(save_layout)

        # --- Right: Lye Solution Utility ---
        lye_widget = QWidget()
        lye_layout = QVBoxLayout(lye_widget)
        lye_layout.setContentsMargins(10, 0, 0, 0)

        lye_layout.addWidget(QLabel("<b>Lye Solution Mixer</b>"))
        lye_layout.addWidget(
            QLabel("Calculate how to make a Master Batch Lye Solution.")
        )

        form = QFormLayout()

        self.target_weight_spin = QDoubleSpinBox()
        self.target_weight_spin.setRange(0, 100000)
        self.target_weight_spin.setValue(1000)
        self.target_weight_spin.setSuffix(" g")
        self.target_weight_spin.valueChanged.connect(self.calc_lye_mix)
        form.addRow("Target Solution Weight:", self.target_weight_spin)

        self.concentration_spin = QDoubleSpinBox()
        self.concentration_spin.setRange(1, 99)
        self.concentration_spin.setValue(50.0)
        self.concentration_spin.setSuffix("%")
        self.concentration_spin.valueChanged.connect(self.calc_lye_mix)
        form.addRow("Desired Concentration:", self.concentration_spin)

        lye_layout.addLayout(form)

        self.lye_result_lbl = QLabel("Mix:\n500g Lye\n500g Water")
        self.lye_result_lbl.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 10px; border: 1px solid #555;"
        )
        lye_layout.addWidget(self.lye_result_lbl)

        lye_layout.addStretch()

        splitter.addWidget(oil_widget)
        splitter.addWidget(lye_widget)
        layout.addWidget(splitter)

        self.setLayout(layout)
        self.blend_oils = {}  # Name -> Percent

    def add_oil_to_blend(self):
        oil = self.oil_combo.currentText()
        pct = self.percent_spin.value()

        if pct <= 0:
            return

        if oil in self.blend_oils:
            self.blend_oils[oil] += pct
        else:
            self.blend_oils[oil] = pct

        self.update_blend_table()

    def update_blend_table(self):
        self.blend_table.setRowCount(len(self.blend_oils))
        total = 0.0
        for r, (oil, pct) in enumerate(self.blend_oils.items()):
            self.blend_table.setItem(r, 0, QTableWidgetItem(oil))
            self.blend_table.setItem(r, 1, QTableWidgetItem(f"{pct:.2f}%"))
            total += pct

        self.total_lbl.setText(f"Total: {total:.2f}%")
        if abs(total - 100.0) > 0.1:
            self.total_lbl.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.total_lbl.setStyleSheet("color: green; font-weight: bold;")

    def save_blend(self):
        name = self.blend_name.currentText().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please name your blend.")
            return

        total = sum(self.blend_oils.values())
        if abs(total - 100.0) > 0.1:
            QMessageBox.warning(
                self, "Error", f"Blend percentages must equal 100% (Current: {total}%)"
            )
            return

        # Calculate composite properties
        composite_sap_naoh = 0.0
        composite_sap_koh = 0.0
        composite_iodine = 0.0
        composite_ins = 0.0
        composite_fa = {}

        for oil_name, pct in self.blend_oils.items():
            oil_data = get_oil_info(oil_name)
            if not oil_data:
                continue

            ratio = pct / 100.0
            # Use sap_naoh as primary key, fallback to sap if missing
            sap_val = oil_data.get("sap_naoh", oil_data.get("sap", 0))
            composite_sap_naoh += sap_val * ratio
            # Some data sources might store sap_koh differently, assuming standard conversion if missing
            sap_koh = oil_data.get("sap_koh", sap_val * 1.403)
            composite_sap_koh += sap_koh * ratio
            composite_iodine += oil_data.get("iodine", 0) * ratio
            composite_ins += oil_data.get("ins", 0) * ratio

            for fa, val in oil_data.get("fa", {}).items():
                composite_fa[fa] = composite_fa.get(fa, 0) + (val * ratio)

        # Calculate qualities from FA
        qualities = _calc_qualities(composite_fa)

        new_oil_data = {
            "sap_naoh": composite_sap_naoh,
            "sap_koh": composite_sap_koh,
            "iodine": composite_iodine,
            "ins": composite_ins,
            "fa": composite_fa,
            "qualities": qualities,
            "description": "Master Batch Blend",
        }

        save_custom_oil(name, new_oil_data)
        QMessageBox.information(
            self,
            "Success",
            f"Saved '{name}' to custom oils.\nYou can now select it in the Recipe Calculator.",
        )
        self.blend_oils.clear()
        self.update_blend_table()

    def calc_lye_mix(self):
        total = self.target_weight_spin.value()
        conc = self.concentration_spin.value() / 100.0

        if conc <= 0:
            return

        lye = total * conc
        water = total - lye

        self.lye_result_lbl.setText(f"Mix:\n{lye:.1f} g Lye\n{water:.1f} g Water")
