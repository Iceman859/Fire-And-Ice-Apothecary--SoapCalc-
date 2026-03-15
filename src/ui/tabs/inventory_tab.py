"""UI INVENTORY TAB - Manage ingredient costs and inventory"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QCompleter,
    QGroupBox,
    QGridLayout,
    QMessageBox,
    QAbstractItemView,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from src.data import get_all_oil_names
from src.data.additives import (
    get_all_additive_names,
)


class InventoryCostWidget(QWidget):
    """Widget for managing ingredient costs"""

    costs_changed = pyqtSignal()

    def __init__(self, cost_manager):
        super().__init__()
        self.cost_manager = cost_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Low Stock Settings
        alert_layout = QHBoxLayout()
        alert_layout.addWidget(QLabel("Low Stock Alert Threshold:"))
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0, 10000)
        self.threshold_spin.setValue(100.0)  # Default 100 units
        self.threshold_spin.valueChanged.connect(self.refresh_table)
        alert_layout.addWidget(self.threshold_spin)

        alert_layout.addStretch()
        self.total_value_label = QLabel("Total Inventory Value: $0.00")
        self.total_value_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #4caf50;"
        )
        alert_layout.addWidget(self.total_value_label)
        layout.addLayout(alert_layout)

        # Input Form Group
        form_group = QGroupBox("Update Ingredient Cost")
        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Ingredient:"), 0, 0)
        self.ingredient_combo = QComboBox()
        self.ingredient_combo.setEditable(True)
        # Populate with oils and additives
        items = sorted(
            get_all_oil_names() + get_all_additive_names() + ["NaOH", "KOH", "90% KOH"]
        )
        self.ingredient_combo.addItems(items)
        completer = QCompleter(items)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.ingredient_combo.setCompleter(completer)

        form_layout.addWidget(self.ingredient_combo, 0, 1)

        form_layout.addWidget(QLabel("Price Paid ($):"), 1, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 10000)
        self.price_spin.setDecimals(2)
        form_layout.addWidget(self.price_spin, 1, 1)

        form_layout.addWidget(QLabel("Quantity:"), 2, 0)
        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0, 10000)
        self.qty_spin.setDecimals(2)
        form_layout.addWidget(self.qty_spin, 2, 1)

        form_layout.addWidget(QLabel("Unit:"), 3, 0)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(
            ["grams", "oz", "lbs", "kg", "liters", "gallons", "fl oz"]
        )
        form_layout.addWidget(self.unit_combo, 3, 1)

        # Buttons
        btn_layout = QHBoxLayout()

        clear_btn = QPushButton("Clear Form")
        clear_btn.clicked.connect(self.clear_form)
        btn_layout.addWidget(clear_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_cost)
        delete_btn.setStyleSheet("background-color: #d32f2f; color: white;")
        btn_layout.addWidget(delete_btn)

        save_btn = QPushButton("Save / Update")
        save_btn.clicked.connect(self.save_cost)
        save_btn.setStyleSheet("background-color: #388e3c; color: white;")
        btn_layout.addWidget(save_btn)

        restock_btn = QPushButton("Restock (Add)")
        restock_btn.setToolTip("Add to existing inventory (Weighted Average Cost)")
        restock_btn.clicked.connect(self.restock_inventory)
        restock_btn.setStyleSheet("background-color: #1976d2; color: white;")
        btn_layout.addWidget(restock_btn)

        form_layout.addLayout(btn_layout, 4, 0, 1, 2)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Table
        self.cost_table = QTableWidget()
        self.cost_table.setColumnCount(5)
        self.cost_table.setHorizontalHeaderLabels(
            ["Ingredient", "Price", "Quantity", "Cost/g", "Cost/oz"]
        )
        self.cost_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.cost_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.cost_table.itemSelectionChanged.connect(self.load_selected_item)
        layout.addWidget(self.cost_table)

        self.refresh_table()

        self.setLayout(layout)

    def save_cost(self):
        name = self.ingredient_combo.currentText()
        price = self.price_spin.value()
        qty = self.qty_spin.value()
        unit = self.unit_combo.currentText()

        if name and qty > 0:
            self.cost_manager.set_cost(name, price, qty, unit)
            self.refresh_table()
            self.clear_form()
            self.costs_changed.emit()

    def restock_inventory(self):
        """Add to existing inventory (Weighted Average)"""
        name = self.ingredient_combo.currentText()
        price = self.price_spin.value()
        qty = self.qty_spin.value()
        unit = self.unit_combo.currentText()

        if name and qty > 0:
            self.cost_manager.add_stock(name, price, qty, unit)
            self.refresh_table()
            self.clear_form()
            self.costs_changed.emit()

    def delete_cost(self):
        """Delete selected cost item"""
        row = self.cost_table.currentRow()
        if row < 0:
            return

        name = self.cost_table.item(row, 0).text()
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}' from inventory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if name in self.cost_manager.costs:
                del self.cost_manager.costs[name]
                # Try to persist changes
                if hasattr(self.cost_manager, "save_costs"):
                    self.cost_manager.save_costs()
                elif hasattr(self.cost_manager, "save"):
                    self.cost_manager.save()

                self.refresh_table()
                self.clear_form()
                self.costs_changed.emit()

    def load_selected_item(self):
        """Load selected item into form for editing"""
        row = self.cost_table.currentRow()
        if row >= 0:
            name_item = self.cost_table.item(row, 0)
            if name_item:
                name = name_item.text()
                if name in self.cost_manager.costs:
                    data = self.cost_manager.costs[name]
                    self.ingredient_combo.setCurrentText(name)
                    self.price_spin.setValue(float(data.get("price", 0.0)))
                    self.qty_spin.setValue(float(data.get("quantity", 0.0)))

                    unit = data.get("unit", "grams")
                    index = self.unit_combo.findText(unit)
                    if index >= 0:
                        self.unit_combo.setCurrentIndex(index)

    def clear_form(self):
        """Clear the input form"""
        self.ingredient_combo.setCurrentIndex(-1)
        self.price_spin.setValue(0.0)
        self.qty_spin.setValue(0.0)
        self.unit_combo.setCurrentIndex(0)
        self.cost_table.clearSelection()

    def refresh_table(self):
        self.cost_table.setRowCount(0)
        costs = self.cost_manager.costs
        self.cost_table.setRowCount(len(costs))

        threshold = self.threshold_spin.value()

        total_value = self.cost_manager.get_total_inventory_value()
        self.total_value_label.setText(f"Total Inventory Value: ${total_value:,.2f}")

        for i, (name, data) in enumerate(sorted(costs.items())):
            price = data.get("price", 0.0)
            qty = float(data.get("quantity", 0.0))
            unit = data.get("unit", "")
            cost_per_g = self.cost_manager.get_cost_per_gram(name)
            cost_per_oz = cost_per_g * 28.3495

            # Determine color (Orange if low stock)
            text_color = QColor("#ff9800") if qty < threshold else QColor("#e0e0e0")

            self.cost_table.setItem(i, 0, QTableWidgetItem(name))
            self.cost_table.setItem(i, 1, QTableWidgetItem(f"${price:.2f}"))
            self.cost_table.setItem(i, 2, QTableWidgetItem(f"{qty:.2f} {unit}"))
            self.cost_table.setItem(i, 3, QTableWidgetItem(f"${cost_per_g:.2f}"))
            self.cost_table.setItem(i, 4, QTableWidgetItem(f"${cost_per_oz:.2f}"))

            for col in range(5):
                self.cost_table.item(i, col).setForeground(text_color)

    def refresh_ingredients(self):
        """Refresh ingredient list"""
        current = self.ingredient_combo.currentText()
        self.ingredient_combo.clear()
        items = sorted(
            get_all_oil_names() + get_all_additive_names() + ["NaOH", "KOH", "90% KOH"]
        )
        self.ingredient_combo.addItems(items)
        self.ingredient_combo.setCurrentText(current)

        completer = QCompleter(items)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.ingredient_combo.setCompleter(completer)
