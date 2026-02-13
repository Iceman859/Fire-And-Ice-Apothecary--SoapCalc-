from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QDoubleSpinBox, QPushButton, QTabWidget, QWidget, 
    QFormLayout, QMessageBox, QCheckBox, QGroupBox
)
from src.data.oils import save_custom_oil, delete_custom_oil, _calc_qualities
from src.data.additives import add_additive_entry, remove_additive_entry

class IngredientEditorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Ingredient Editor")
        self.setFixedSize(500, 650)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # --- Custom Oil Tab ---
        oil_tab = QWidget()
        oil_layout = QVBoxLayout()
        
        form = QFormLayout()
        self.oil_name = QLineEdit()
        self.oil_name.setPlaceholderText("e.g. My Infused Olive Oil")
        form.addRow("Oil Name:", self.oil_name)
        
        self.sap_naoh = QDoubleSpinBox()
        self.sap_naoh.setDecimals(3)
        self.sap_naoh.setRange(0, 1.0)
        form.addRow("SAP (NaOH):", self.sap_naoh)
        
        self.sap_koh = QDoubleSpinBox()
        self.sap_koh.setDecimals(3)
        self.sap_koh.setRange(0, 1.0)
        form.addRow("SAP (KOH):", self.sap_koh)
        
        self.iodine = QDoubleSpinBox()
        self.iodine.setRange(0, 200)
        form.addRow("Iodine:", self.iodine)
        
        self.ins = QDoubleSpinBox()
        self.ins.setRange(0, 300)
        form.addRow("INS:", self.ins)
        
        oil_layout.addLayout(form)
        
        # Fatty Acids
        fa_group = QGroupBox("Fatty Acid Profile (Must sum to ~100%)")
        fa_layout = QFormLayout()
        self.fa_inputs = {}
        for fa in ["lauric", "myristic", "palmitic", "stearic", "ricinoleic", "oleic", "linoleic", "linolenic"]:
            spin = QDoubleSpinBox()
            spin.setRange(0, 100)
            fa_layout.addRow(f"{fa.capitalize()}:", spin)
            self.fa_inputs[fa] = spin
        fa_group.setLayout(fa_layout)
        oil_layout.addWidget(fa_group)
        
        btn_layout = QHBoxLayout()
        save_oil_btn = QPushButton("Save Oil")
        save_oil_btn.clicked.connect(self.save_oil)
        btn_layout.addWidget(save_oil_btn)
        
        del_oil_btn = QPushButton("Delete Oil (by Name)")
        del_oil_btn.clicked.connect(self.delete_oil)
        btn_layout.addWidget(del_oil_btn)
        
        oil_layout.addLayout(btn_layout)
        oil_tab.setLayout(oil_layout)
        tabs.addTab(oil_tab, "Custom Oil")
        
        # --- Custom Additive Tab ---
        add_tab = QWidget()
        add_layout = QVBoxLayout()
        
        add_form = QFormLayout()
        self.add_name = QLineEdit()
        self.add_name.setPlaceholderText("e.g. Aloe Vera Juice")
        add_form.addRow("Additive Name:", self.add_name)
        
        self.add_desc = QLineEdit()
        add_form.addRow("Description:", self.add_desc)
        
        self.water_adjust = QDoubleSpinBox()
        self.water_adjust.setRange(-100, 100)
        self.water_adjust.setToolTip("Percentage to adjust water calculation (usually 0)")
        add_form.addRow("Water % Adjust:", self.water_adjust)
        
        self.default_pct = QDoubleSpinBox()
        self.default_pct.setRange(0, 100)
        self.default_pct.setValue(1.0)
        add_form.addRow("Default Usage %:", self.default_pct)
        
        self.is_water_replace = QCheckBox("Is Water Replacement?")
        self.is_water_replace.setToolTip("If checked, the weight of this additive is subtracted from the total water.")
        add_form.addRow("", self.is_water_replace)
        
        add_layout.addLayout(add_form)
        add_layout.addStretch()
        
        add_btn_layout = QHBoxLayout()
        save_add_btn = QPushButton("Save Additive")
        save_add_btn.clicked.connect(self.save_additive)
        add_btn_layout.addWidget(save_add_btn)
        
        del_add_btn = QPushButton("Delete Additive (by Name)")
        del_add_btn.clicked.connect(self.delete_additive)
        add_btn_layout.addWidget(del_add_btn)
        
        add_layout.addLayout(add_btn_layout)
        add_tab.setLayout(add_layout)
        tabs.addTab(add_tab, "Custom Additive")
        
        layout.addWidget(tabs)
        self.setLayout(layout)

    def save_oil(self):
        name = self.oil_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Oil name is required.")
            return
            
        fa = {k: spin.value() for k, spin in self.fa_inputs.items()}
        
        # Auto-calculate qualities from FA
        qualities = _calc_qualities(fa)
        
        data = {
            "sap_naoh": self.sap_naoh.value(),
            "sap_koh": self.sap_koh.value(),
            "iodine": self.iodine.value(),
            "ins": self.ins.value(),
            "fa": fa,
            "qualities": qualities
        }
        
        save_custom_oil(name, data)
        QMessageBox.information(self, "Success", f"Saved custom oil: {name}\nRestart app or refresh lists to see changes.")

    def delete_oil(self):
        name = self.oil_name.text().strip()
        if not name:
            return
        delete_custom_oil(name)
        QMessageBox.information(self, "Success", f"Deleted oil: {name}")

    def save_additive(self):
        name = self.add_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Additive name is required.")
            return
            
        data = {
            "description": self.add_desc.text(),
            "water_percent_adjust": self.water_adjust.value(),
            "default_percent_of_oils": self.default_pct.value(),
            "is_water_replacement": self.is_water_replace.isChecked()
        }
        
        add_additive_entry(name, data)
        QMessageBox.information(self, "Success", f"Saved custom additive: {name}\nRestart app or refresh lists to see changes.")

    def delete_additive(self):
        name = self.add_name.text().strip()
        if not name:
            return
        remove_additive_entry(name)
        QMessageBox.information(self, "Success", f"Deleted additive: {name}")