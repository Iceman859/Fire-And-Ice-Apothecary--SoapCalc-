from PyQt6.QtCore import QAbstractTableModel, Qt
from src.utils.logger import log

class RecipeTableModel(QAbstractTableModel):
    """Model to handle the oils list in the recipe tab."""

    def __init__(self, calculator, controller=None):
        super().__init__()
        self.calculator = calculator
        self.controller = controller # Need reference to trigger updates
        self.unit_system = "grams"
        self.cost_manager = None
        self.headers = ["Oil Name", "Weight", "Unit", "%", "Cost"]

    def rowCount(self, parent=None):
        return len(self.calculator.oils)

    def columnCount(self, parent=None):
        return len(self.headers)

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section] if section < len(self.headers) else None
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        oil_names = list(self.calculator.oils.keys())
        if index.row() >= len(oil_names):
            return None

        oil_name = oil_names[index.row()]
        weight_grams = self.calculator.oils.get(oil_name, 0.0)
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return oil_name

            if col == 1: # Weight
                unit = getattr(self, 'unit_system', 'grams')
                if unit == 'ounces':
                    return f"{weight_grams / 28.3495231:.2f}"
                if unit == 'pounds':
                    return f"{weight_grams / 453.592:.3f}"
                return f"{weight_grams:.2f}"

            if col == 2: # Unit Label
                unit = getattr(self, 'unit_system', 'grams')
                if unit == 'ounces': return "oz"
                if unit == 'pounds': return "lb"
                return "g"

            if col == 3: # Percentage
                total = self.calculator.get_total_oil_weight()
                return f"{(weight_grams / total * 100):.1f}%" if total > 0 else "0%"

            if col == 4: # Cost
                if self.cost_manager:
                    cost_per_g = self.cost_manager.get_cost_per_gram(oil_name)
                    total_cost = cost_per_g * weight_grams
                    return f"${total_cost:.2f}"
                return "$0.00"

        return None

    def flags(self, index):
        # Column 1 (Weight) and Column 3 (%) should be editable
        if index.column() in [1, 3]:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole:
            return False

        try:
            val = float(value)
            oil_names = list(self.calculator.oils.keys())
            if index.row() >= len(oil_names):
                return False

            name = oil_names[index.row()]

            if index.column() == 1: # Editing Weight
                # Convert UI value back to grams for the calculator
                if self.unit_system == "ounces":
                    grams = val * 28.3495231
                elif self.unit_system == "pounds":
                    grams = val * 453.592
                else:
                    grams = val

                self.calculator.add_oil(name, grams) # Updates internal dict

            elif index.column() == 3: # Editing Percentage
                self.calculator.rebalance_oils(name, val)

            # Signal that data changed so the table redraws
            self.layoutChanged.emit()

            # TRIGGER THE REFRESH: This ensures the Controller updates labels
            if self.controller:
                self.controller.update_calculations()

            return True

        except (ValueError, AttributeError, ZeroDivisionError) as e:
            log.error(f"Error updating table data: {e}")
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