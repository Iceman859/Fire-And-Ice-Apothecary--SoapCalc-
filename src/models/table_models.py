from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from src.utils.logger import log

class RecipeTableModel(QAbstractTableModel):
    """Model to handle the oils list in the recipe tab."""
    def __init__(self, calculator, controller=None, cost_manager=None):
        super().__init__()
        self.calculator = calculator
        self.controller = controller
        self.cost_manager = cost_manager  # <-- Now it gets set!
        self.unit_system = "grams"
        self.headers = ["Lock", "Oil Name", "Weight", "Unit", "%", "Cost"]

    def rowCount(self, parent=None):
        return len(self.calculator.oils)

    def columnCount(self, parent=None):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section] if section < len(self.headers) else None
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        col = index.column()

        # COLUMN 0: THE LOCK CHECKBOX
        if col == 0:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable

        # COLUMN 2 (Weight) and COLUMN 4 (%) are editable text
        if col in [2, 4]:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        oil_names = list(self.calculator.oils.keys())
        if index.row() >= len(oil_names):
            return None

        oil_name = oil_names[index.row()]
        weight_grams = self.calculator.oils.get(oil_name, 0.0)
        col = index.column()

        if col == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                return Qt.CheckState.Checked if oil_name in self.calculator.locked_oils else Qt.CheckState.Unchecked
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 1: return oil_name

            if col == 2: # Weight Display
                if self.unit_system == "ounces":
                    return f"{(weight_grams * 0.035274):.2f}"
                if self.unit_system == "pounds":
                    return f"{(weight_grams * 0.00220462):.2f}"
                return f"{weight_grams:.2f}"

            if col == 3: # Unit String
                if self.unit_system == "ounces": return "oz"
                if self.unit_system == "pounds": return "lb"
                return "g"

            if col == 4: # Percentage
                total = sum(self.calculator.oils.values())
                return f"{(weight_grams / total * 100):.2f}%" if total > 0 else "0.00%"

            if col == 5: # Cost
                if self.cost_manager:
                    cost = self.cost_manager.get_cost_per_gram(oil_name) * weight_grams
                    return f"${cost:.2f}"
                return "$0.00"

        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        oil_names = list(self.calculator.oils.keys())
        oil_name = oil_names[index.row()] # Define oil_name here
        col = index.column()

        try:
            if role == Qt.ItemDataRole.EditRole:
                # Clean the input
                val_str = str(value).replace('%', '').strip()
                if not val_str: return False
                val = float(val_str)

                if col == 4:  # PERCENT COLUMN
                    self.calculator.rebalance_oils(oil_name, val)

                elif col == 2:  # WEIGHT COLUMN
                    if self.unit_system == "ounces":
                        val = val / 0.035274
                    self.calculator.oils[oil_name] = val

                if self.controller:
                    self.controller.update_calculations()

                self.layoutChanged.emit()
                return True

            if role == Qt.ItemDataRole.CheckStateRole and col == 0:
                is_locked = (value == Qt.CheckState.Checked.value)
                self.calculator.toggle_lock(oil_name, is_locked)
                self.dataChanged.emit(index, index)
                return True

        except Exception as e:
            log.error(f"Error in setData: {e}")
            return False
        return False

    def refresh(self):
        """Force the view to refresh all rows after a large data change (like loading)."""
        self.beginResetModel()
        self.endResetModel()

    def get_row_data(self, row):
        """Helper for the controller to pull data reliably during sync."""
        oil_names = list(self.calculator.oils.keys())
        if 0 <= row < len(oil_names):
            name = oil_names[row]
            return {
                'name': name,
                'weight': self.calculator.oils[name]
            }
        return {'name': None, 'weight': 0}

    def removeRow(self, row, parent=None):
            """Removes an oil from the calculator and updates the table view."""
            if parent is None:
                parent = QModelIndex()

            self.beginRemoveRows(parent, row, row)

            # Get the list of oil names currently in the calculator
            oil_names = list(self.calculator.oils.keys())

            if 0 <= row < len(oil_names):
                oil_to_remove = oil_names[row]
                # Delete it from the actual data source
                if oil_to_remove in self.calculator.oils:
                    del self.calculator.oils[oil_to_remove]

            self.endRemoveRows()
            return True