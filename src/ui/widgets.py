"""UI Widgets"""

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
    QSpinBox,
    QCompleter,
    QGroupBox,
    QGridLayout,
    QTextEdit,
    QTextBrowser,
    QFormLayout,
    QMessageBox,
    QAbstractItemView,
    QInputDialog,
    QLineEdit,
)
from PyQt6.QtCore import pyqtSignal, Qt, QSettings
from PyQt6.QtGui import QColor
from src.models import SoapCalculator, RecipeManager
from src.data import get_all_oil_names
from src.data.additives import get_all_additive_names
from datetime import datetime

# optional matplotlib for charts
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    _HAS_MATPLOTLIB = True
except Exception:
    FigureCanvas = None
    Figure = None
    _HAS_MATPLOTLIB = False

# optional print support
try:
    from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

    _HAS_PRINTER = True
except ImportError:
    _HAS_PRINTER = False


class OilInputWidget(QWidget):
    """Widget for adding oils to recipe"""

    oil_added = pyqtSignal()

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.target_weight_callback = None
        self.setup_ui()

    def setup_ui(self):
        """Setup oil input controls"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Oil selection
        layout.addWidget(QLabel("Oil:"))
        self.oil_combo = QComboBox()
        self.oil_combo.setEditable(True)
        names = get_all_oil_names()
        self.oil_combo.addItems(names)
        # simple completion
        self.oil_combo.setCurrentIndex(-1)  # Start blank
        completer = QCompleter(names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.oil_combo.setCompleter(completer)
        layout.addWidget(self.oil_combo, 2)

        # Weight input with unit selector
        self.weight_label = QLabel("Weight:")
        layout.addWidget(self.weight_label)
        self.weight_spinbox = QDoubleSpinBox()
        self.weight_spinbox.setRange(0, 10000)
        self.weight_spinbox.setValue(0)
        layout.addWidget(self.weight_spinbox, 1)

        self.weight_unit_combo = QComboBox()
        self.weight_unit_combo.addItems(["g", "oz", "lbs", "%"])
        self.weight_unit_combo.currentTextChanged.connect(self.on_unit_changed)
        self.weight_unit_combo.setFixedWidth(60)
        layout.addWidget(self.weight_unit_combo)

        # Add button
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_oil)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def add_oil(self):
        """Add selected oil to recipe"""
        oil_name = self.oil_combo.currentText()
        weight = self.weight_spinbox.value()
        unit = self.weight_unit_combo.currentText()

        if weight > 0:
            weight_grams = 0.0
            if unit == "%":
                if self.target_weight_callback:
                    total_grams = self.target_weight_callback()
                    weight_grams = total_grams * (weight / 100.0)
            else:
                unit_map = {"g": "grams", "oz": "ounces", "lbs": "pounds"}
                weight_grams = self.calculator.convert_to_grams(weight, unit_map[unit])

            if weight_grams > 0:
                self.calculator.add_oil(oil_name, weight_grams)
            self.weight_spinbox.setValue(0)
            self.oil_added.emit()

    def set_unit_system(self, unit_system: str):
        """Update default unit selection based on global settings"""
        unit_map = {"grams": "g", "ounces": "oz", "pounds": "lbs"}
        self.weight_unit_combo.setCurrentText(unit_map.get(unit_system, "g"))

    def on_unit_changed(self, text: str):
        """Update label and range based on unit selection"""
        if text == "%":
            self.weight_label.setText("Percent:")
            self.weight_spinbox.setRange(0, 100)
        else:
            self.weight_label.setText("Weight:")
            self.weight_spinbox.setRange(0, 10000)

    def refresh_oils(self):
        """Refresh the oil list from database"""
        current = self.oil_combo.currentText()
        self.oil_combo.clear()
        names = get_all_oil_names()
        self.oil_combo.addItems(names)
        self.oil_combo.setCurrentText(current)

        completer = QCompleter(names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.oil_combo.setCompleter(completer)


class AdditiveInputWidget(QWidget):
    """Widget for adding recipe additives"""

    additive_added = pyqtSignal()

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Additive:"))
        self.add_combo = QComboBox()
        self.add_combo.setEditable(True)
        additive_names = get_all_additive_names()
        self.add_combo.addItems(additive_names)
        self.add_combo.setCurrentIndex(-1)  # Start blank
        completer = QCompleter(additive_names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.add_combo.setCompleter(completer)
        layout.addWidget(self.add_combo, 2)

        # Amount type selector: percent of oils or explicit weight
        self.amount_type_combo = QComboBox()
        self.amount_type_combo.addItems(["% of Oils", "Weight"])
        self.amount_type_combo.currentTextChanged.connect(self.on_amount_type_changed)
        layout.addWidget(self.amount_type_combo)

        # Percent input (default)
        self.percent_widget = QWidget()
        p_layout = QHBoxLayout(self.percent_widget)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_layout.addWidget(QLabel("%:"))
        self.add_spin = QDoubleSpinBox()
        self.add_spin.setRange(0, 100)
        self.add_spin.setSingleStep(0.5)
        self.add_spin.setValue(0)
        p_layout.addWidget(self.add_spin)
        layout.addWidget(self.percent_widget)

        # Weight input (hidden by default)
        self.weight_widget = QWidget()
        w_layout = QHBoxLayout(self.weight_widget)
        w_layout.setContentsMargins(0, 0, 0, 0)
        w_layout.addWidget(QLabel("Amt:"))
        self.add_weight_spin = QDoubleSpinBox()
        self.add_weight_spin.setRange(0, 10000)
        self.add_weight_spin.setSingleStep(1.0)
        self.add_weight_spin.setValue(0.0)
        w_layout.addWidget(self.add_weight_spin)
        self.add_unit_combo = QComboBox()
        self.add_unit_combo.addItems(["g", "oz", "lbs"])
        self.add_unit_combo.setFixedWidth(60)
        w_layout.addWidget(self.add_unit_combo)

        self.weight_widget.setVisible(False)
        layout.addWidget(self.weight_widget)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_additive)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def add_additive(self):
        name = self.add_combo.currentText()
        amt_type = self.amount_type_combo.currentText()
        total_oil = self.calculator.get_total_oil_weight()
        amount_grams = 0.0
        if amt_type == "% of Oils":
            percent = self.add_spin.value()
            amount_grams = (percent / 100.0) * total_oil if total_oil > 0 else 0.0
        else:
            val = self.add_weight_spin.value()
            unit = self.add_unit_combo.currentText()
            unit_map = {"g": "grams", "oz": "ounces", "lbs": "pounds"}
            amount_grams = self.calculator.convert_to_grams(val, unit_map[unit])

        if amount_grams > 0:
            self.calculator.add_additive(name, amount_grams)
            # reset inputs
            self.add_spin.setValue(0)
            self.add_weight_spin.setValue(0)
            self.additive_added.emit()

    def on_amount_type_changed(self, text: str):
        """Show/hide percent vs weight inputs"""
        if text == "% of Oils":
            self.percent_widget.setVisible(True)
            self.weight_widget.setVisible(False)
        else:
            self.percent_widget.setVisible(False)
            self.weight_widget.setVisible(True)

    def set_unit_system(self, unit_system: str):
        """Update default unit selection based on global settings"""
        unit_map = {"grams": "g", "ounces": "oz", "pounds": "lbs"}
        self.add_unit_combo.setCurrentText(unit_map.get(unit_system, "g"))

    def refresh_additives(self):
        """Refresh the additive list from database"""
        current = self.add_combo.currentText()
        self.add_combo.clear()
        names = get_all_additive_names()
        self.add_combo.addItems(names)
        self.add_combo.setCurrentText(current)

        completer = QCompleter(names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.add_combo.setCompleter(completer)


class FragranceWidget(QWidget):
    """Widget to calculate fragrance amount based on usage rate"""

    fragrance_added = pyqtSignal()

    def __init__(self, calculator: SoapCalculator, cost_manager=None):
        super().__init__()
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.setup_ui()

    def setup_ui(self):
        group = QGroupBox("Fragrance / Essential Oil Calculator")
        layout = QGridLayout()

        layout.addWidget(QLabel("Scent Name:"), 0, 0)
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)

        # Populate with inventory items if available, otherwise defaults
        items = [
            "Lavender EO",
            "Peppermint EO",
            "Tea Tree EO",
            "Lemon EO",
            "Orange EO",
            "Fragrance Oil",
        ]
        if self.cost_manager:
            # Add items from inventory that aren't already in the list
            inventory_items = sorted(self.cost_manager.costs.keys())
            items = sorted(list(set(items + inventory_items)))

        self.name_combo.addItems(items)
        self.name_combo.setPlaceholderText("e.g. Lavender EO")
        self.name_combo.setCurrentIndex(-1)
        layout.addWidget(self.name_combo, 0, 1)

        layout.addWidget(QLabel("Usage Rate:"), 1, 0)

        # Rate input with unit selector
        rate_layout = QHBoxLayout()
        rate_layout.setContentsMargins(0, 0, 0, 0)
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setSuffix("")
        self.rate_spin.setToolTip("Default: 0.5 oz/lb")
        self.rate_spin.setRange(0, 10)
        self.rate_spin.setSingleStep(0.05)
        self.rate_spin.setValue(0.50)
        self.rate_spin.valueChanged.connect(self.update_calculation)
        rate_layout.addWidget(self.rate_spin)
        self.rate_unit_combo = QComboBox()
        self.rate_unit_combo.addItems(["%", "oz/lb", "g/kg"])
        self.rate_unit_combo.setCurrentText("oz/lb")
        self.rate_unit_combo.currentTextChanged.connect(self.on_rate_unit_changed)
        rate_layout.addWidget(self.rate_unit_combo)
        layout.addLayout(rate_layout, 1, 1)

        layout.addWidget(QLabel("Required Amount:"), 2, 0)
        self.amount_lbl = QLabel("0.00 g")
        self.amount_lbl.setStyleSheet("font-weight: bold; color: #4fc3f7;")
        layout.addWidget(self.amount_lbl, 2, 1)

        add_btn = QPushButton("Add to Additives")
        add_btn.clicked.connect(self.add_fragrance)
        layout.addWidget(add_btn, 3, 0, 1, 2)

        group.setLayout(layout)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

    def on_rate_unit_changed(self, unit: str):
        """Update spinbox settings and defaults based on unit"""
        self.rate_spin.blockSignals(True)
        if unit == "%":
            self.rate_spin.setSuffix("%")
            self.rate_spin.setRange(0, 100)
            self.rate_spin.setValue(3.0)  # Change this value to match your default
            self.rate_spin.setToolTip("Typical: 3-6%")
        elif unit == "oz/lb":
            self.rate_spin.setSuffix("")
            self.rate_spin.setRange(0, 10)
            self.rate_spin.setValue(0.5)  # SoapCalc Default
            self.rate_spin.setToolTip("SoapCalc Default: 0.5 oz/lb")
        elif unit == "g/kg":
            self.rate_spin.setSuffix("")
            self.rate_spin.setRange(0, 1000)
            self.rate_spin.setValue(31.0)  # SoapCalc Default
            self.rate_spin.setToolTip("SoapCalc Default: 31 g/kg")
        self.rate_spin.blockSignals(False)
        self.update_calculation()

    def update_calculation(self):
        """Recalculate amount based on current total oils"""
        rate = self.rate_spin.value()
        unit_mode = self.rate_unit_combo.currentText()
        total_oil = self.calculator.get_total_oil_weight()
        amount_grams = total_oil * (rate / 100.0)

        amount_grams = 0.0
        if unit_mode == "%":
            amount_grams = total_oil * (rate / 100.0)
        elif unit_mode == "oz/lb":
            # Convert total oil to lbs, multiply by rate (oz), convert result to grams
            total_lbs = total_oil / 453.592
            amount_oz = total_lbs * rate
            amount_grams = amount_oz * 28.3495
        elif unit_mode == "g/kg":
            # Convert total oil to kg, multiply by rate
            total_kg = total_oil / 1000.0
            amount_grams = total_kg * rate

        unit = self.calculator.unit_system
        display_amount = self.calculator.convert_weight(amount_grams, unit)
        abbr = self.calculator.get_unit_abbreviation()

        self.amount_lbl.setText(f"{display_amount:.2f} {abbr}")

    def add_fragrance(self):
        rate = self.rate_spin.value()
        unit_mode = self.rate_unit_combo.currentText()
        total_oil = self.calculator.get_total_oil_weight()
        amount_grams = total_oil * (rate / 100.0)

        amount_grams = 0.0
        if unit_mode == "%":
            amount_grams = total_oil * (rate / 100.0)
        elif unit_mode == "oz/lb":
            total_lbs = total_oil / 453.592
            amount_oz = total_lbs * rate
            amount_grams = amount_oz * 28.3495
        elif unit_mode == "g/kg":
            total_kg = total_oil / 1000.0
            amount_grams = total_kg * rate

        if amount_grams > 0:
            name = self.name_combo.currentText()
            if not name:
                name = "Fragrance"

            # Add to calculator additives
            self.calculator.add_additive(name, amount_grams)
            self.fragrance_added.emit()

    def refresh_ingredients(self):
        """Refresh list from cost manager"""
        if self.cost_manager:
            current = self.name_combo.currentText()
            self.name_combo.clear()
            items = [
                "Lavender EO",
                "Peppermint EO",
                "Tea Tree EO",
                "Lemon EO",
                "Orange EO",
                "Fragrance Oil",
            ]
            inventory_items = sorted(self.cost_manager.costs.keys())
            items = sorted(list(set(items + inventory_items)))
            self.name_combo.addItems(items)
            self.name_combo.setCurrentText(current)


class CalculationResultsWidget(QWidget):
    """Widget for displaying calculation results"""

    def __init__(self, calculator: SoapCalculator = None, cost_manager=None):
        super().__init__()
        self.calculator = calculator
        self.cost_manager = cost_manager
        # Cache for internal updates
        self.last_properties = {}
        self.last_unit = "grams"
        self.last_name = None
        self.mb_lye_enabled = False
        self.mb_lye_concentration = 50.0
        self.setup_ui()

    def setup_ui(self):
        """Setup results display"""
        layout = QVBoxLayout()

        # Recipe Name Display
        self.recipe_name_label = QLabel("Unsaved Recipe")
        self.recipe_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.recipe_name_label.font()
        font.setBold(True)
        font.setPointSize(12)
        self.recipe_name_label.setFont(font)
        layout.addWidget(self.recipe_name_label)

        # Batch Weights
        self.weights_group = QGroupBox("Batch Weights")
        w_layout = QGridLayout()

        self.weight_labels = {}
        weight_keys = [
            "Total Oil Weight",
            "Water Weight",
            "Add'l Water",  # Added for MB
            "Lye Weight",
            "Total Batch Weight",
            "Total Batch Cost",
        ]

        for i, key in enumerate(weight_keys):
            w_layout.addWidget(QLabel(f"{key}:"), i, 0)
            val_lbl = QLabel("0.00")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            w_layout.addWidget(val_lbl, i, 1)
            self.weight_labels[key] = val_lbl
        self.weight_labels["Add'l Water"].setVisible(False)  # Hide by default

        self.weights_group.setLayout(w_layout)
        layout.addWidget(self.weights_group)

        # Yield / Bar Estimation
        self.yield_group = QGroupBox("Yield Estimation")
        y_layout = QGridLayout()

        y_layout.addWidget(QLabel("Bar Size:"), 0, 0)
        self.bar_size_spin = QDoubleSpinBox()
        self.bar_size_spin.setRange(0.1, 5000)
        self.bar_size_spin.setSingleStep(0.5)
        self.bar_size_spin.setValue(4.5)
        self.bar_size_spin.valueChanged.connect(
            lambda: self.update_results(
                self.last_properties, self.last_unit, self.last_name
            )
        )
        y_layout.addWidget(self.bar_size_spin, 0, 1)

        self.yield_label = QLabel("0.0 bars")
        y_layout.addWidget(self.yield_label, 0, 2)

        y_layout.addWidget(QLabel("Cost/Bar:"), 1, 0)
        self.cost_per_bar_label = QLabel("$0.00")
        y_layout.addWidget(self.cost_per_bar_label, 1, 1)

        self.yield_group.setLayout(y_layout)
        layout.addWidget(self.yield_group)

        # Predicted Qualities
        self.qualities_group = QGroupBox("Soap Bar Quality")
        self.qualities_group.setToolTip(
            "Theoretical qualities based on oil fatty acid profile.\nThese values do not change with Superfat/Lye Discount."
        )
        q_layout = QGridLayout()

        # Headers
        q_layout.addWidget(QLabel("<b>Quality</b>"), 0, 0)
        q_layout.addWidget(QLabel("<b>Range</b>"), 0, 1)
        q_layout.addWidget(QLabel("<b>Your Recipe</b>"), 0, 2)

        self.quality_labels_display = {}
        # SoapCalc Ranges
        quality_data = [
            ("Hardness", "29 - 54"),
            ("Cleansing", "12 - 22"),
            ("Conditioning", "44 - 69"),
            ("Bubbly", "14 - 46"),
            ("Creamy", "16 - 48"),
            ("Iodine", "41 - 70"),
            ("INS", "136 - 165"),
        ]

        for i, (key, range_val) in enumerate(quality_data):
            row = i + 1
            q_layout.addWidget(QLabel(key), row, 0)
            q_layout.addWidget(QLabel(range_val), row, 1)

            val_lbl = QLabel("0.0")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            q_layout.addWidget(val_lbl, row, 2)
            self.quality_labels_display[key] = val_lbl

        self.qualities_group.setLayout(q_layout)
        layout.addWidget(self.qualities_group)

        layout.addStretch()
        self.setLayout(layout)

    def set_master_batch_mode(self, enabled: bool, concentration: float):
        self.mb_lye_enabled = enabled
        self.mb_lye_concentration = concentration
        self.update_results(self.last_properties, self.last_unit, self.last_name)

    def update_results(
        self, properties: dict, unit_system: str = "grams", recipe_name: str = None
    ):
        """Update displayed results"""
        # Cache values for internal recalculation (e.g. when bar size changes)
        self.last_properties = properties
        self.last_unit = unit_system
        self.last_name = recipe_name

        unit_abbr = {"grams": "g", "ounces": "oz", "pounds": "lbs"}.get(
            unit_system, "g"
        )

        # Update recipe name if provided
        if recipe_name is not None:
            self.recipe_name_label.setText(
                recipe_name if recipe_name else "Unsaved Recipe"
            )

        # Convert values if needed
        def convert_weight(grams):
            if unit_system == "grams":
                return f"{grams:.2f}"
            elif unit_system == "ounces":
                return f"{grams / 28.3495:.2f}"
            elif unit_system == "pounds":
                return f"{grams / 453.592:.2f}"
            return f"{grams:.2f}"

        # Calculate total cost
        total_cost = 0.0
        if self.cost_manager and self.calculator:
            for name, weight in self.calculator.oils.items():
                total_cost += weight * self.cost_manager.get_cost_per_gram(name)
            for name, weight in self.calculator.additives.items():
                total_cost += weight * self.cost_manager.get_cost_per_gram(name)

            # Add Lye Cost
            lye_weight = properties.get("lye_weight", 0.0)
            lye_type = self.calculator.lye_type
            total_cost += lye_weight * self.cost_manager.get_cost_per_gram(lye_type)

        # Handle Master Batch Lye Logic
        display_lye_label = "Lye Weight"
        display_lye_weight = properties["lye_weight"]
        display_water_weight = properties["water_weight"]
        additional_water = 0.0
        show_additional = False

        if self.mb_lye_enabled and self.mb_lye_concentration > 0:
            # Calculate Solution Weight required to get the pure lye amount
            # Weight = Pure Lye / (Concentration %)
            solution_weight = properties["lye_weight"] / (
                self.mb_lye_concentration / 100.0
            )

            # Water contained in that solution
            water_in_solution = solution_weight - properties["lye_weight"]

            # Remaining water needed
            additional_water = properties["water_weight"] - water_in_solution

            display_lye_label = f"Lye Solution ({self.mb_lye_concentration:.0f}%)"
            display_lye_weight = solution_weight
            show_additional = True

            # Note: If additional_water is negative, it means the solution adds too much water
            # The UI will show a negative number, indicating an issue to the user.

        # Calculate Total Weight including Additives (Fragrance, etc.)
        # properties['total_batch_weight'] usually contains just Oils + Water + Lye
        additive_weight = sum(self.calculator.additives.values())
        true_total_weight = properties["total_batch_weight"] + additive_weight

        # Batch Weights
        weights_map = {
            "Total Oil Weight": properties["total_oil_weight"],
            "Water Weight": display_water_weight,  # Original total water
            "Add'l Water": additional_water,
            "Lye Weight": display_lye_weight,
            # Use the true total that includes fragrance
            "Total Batch Weight": true_total_weight,
            "Total Batch Cost": total_cost,
        }

        # Update Labels
        # Update Lye Label text dynamically
        lye_lbl_widget = (
            self.weights_group.layout().itemAtPosition(3, 0).widget()
        )  # Row 3 is Lye
        if lye_lbl_widget:
            lye_lbl_widget.setText(f"{display_lye_label}:")

        # Toggle Additional Water visibility
        self.weight_labels["Add'l Water"].setVisible(show_additional)
        add_water_lbl_widget = self.weights_group.layout().itemAtPosition(2, 0).widget()
        if add_water_lbl_widget:
            add_water_lbl_widget.setVisible(show_additional)
            add_water_lbl_widget.setText("Add'l Water:")

        for key, val in weights_map.items():
            if key in self.weight_labels:
                if key == "Total Batch Cost":
                    self.weight_labels[key].setText(f"${float(val):.2f}")
                else:
                    self.weight_labels[key].setText(
                        f"{convert_weight(val)} {unit_abbr}"
                    )

        # Update Yield Calculation
        bar_size = self.bar_size_spin.value()
        if bar_size > 0:
            # Convert bar size input (which is in display units) to grams for calculation if needed,
            # or just convert total weight to display units.
            # Easier: Convert total weight to display units first.
            total_display_weight = float(convert_weight(true_total_weight))
            bar_count = total_display_weight / bar_size
            self.yield_label.setText(f"Est: {bar_count:.1f} bars")
            self.bar_size_spin.setSuffix(f" {unit_abbr}")

            if bar_count > 0:
                cost_per_bar = total_cost / bar_count
                self.cost_per_bar_label.setText(f"${cost_per_bar:.2f}")
            else:
                self.cost_per_bar_label.setText("$0.00")

        # Soap Qualities
        qualities = properties.get("relative_qualities", {})

        quality_map = {
            "Hardness": qualities.get("hardness", 0),
            "Cleansing": qualities.get("cleansing", 0),
            "Conditioning": qualities.get("conditioning", 0),
            "Bubbly": qualities.get("bubbly", 0),
            "Creamy": qualities.get("creamy", 0),
            "Iodine": qualities.get("iodine", 0),
            "INS": qualities.get("ins", 0),
        }

        for key, val in quality_map.items():
            if key in self.quality_labels_display:
                # SoapCalc uses integers for qualities
                self.quality_labels_display[key].setText(f"{int(round(float(val)))}")


class FABreakdownWidget(QWidget):
    """Displays fatty-acid breakdown as table and chart"""

    def __init__(self, calculator: SoapCalculator = None):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        # Two-column layout: left = table, right = chart
        layout = QHBoxLayout()

        # FA Labels Group (left column)
        self.fa_group = QGroupBox("Fatty Acid Profile")
        fa_layout = QGridLayout()

        self.fa_labels = {}
        order = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "oleic",
            "linoleic",
            "linolenic",
            "ricinoleic",
        ]

        for i, key in enumerate(order):
            fa_layout.addWidget(QLabel(f"{key.capitalize()}:"), i, 0)
            val_lbl = QLabel("0.00%")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            fa_layout.addWidget(val_lbl, i, 1)
            self.fa_labels[key] = val_lbl

        self.fa_group.setLayout(fa_layout)
        layout.addWidget(self.fa_group, 1)

        # Chart area (matplotlib)
        chart_col = QVBoxLayout()
        if _HAS_MATPLOTLIB:
            self.figure = Figure(figsize=(4, 3))
            self.canvas = FigureCanvas(self.figure)
            chart_col.addWidget(self.canvas)
        else:
            chart_col.addWidget(QLabel("Install matplotlib to see chart."))

        layout.addLayout(chart_col, 2)
        self.setLayout(layout)

    def update_fa(self, properties: dict, unit_system: str = "grams"):
        """Update FA breakdown table and chart from properties dict"""
        fa = properties.get("fa_breakdown", {}) if properties else {}
        order = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "oleic",
            "linoleic",
            "linolenic",
            "ricinoleic",
        ]

        values = []
        labels = []
        for key in order:
            # `fa` provided by calculator is already percent (0-100)
            val = float(fa.get(key, 0.0))
            labels.append(key.capitalize())
            values.append(val)

            if key in self.fa_labels:
                self.fa_labels[key].setText(f"{val:.2f}%")

        if _HAS_MATPLOTLIB:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.bar(labels, values, color="#0d47a1")
            ax.set_ylabel("%")
            ax.set_title("Fatty Acid Breakdown")
            # scale y-axis to percent range (0-100) with small padding
            max_val = max(values) if values else 0
            ymax = min(100, max(10, max_val * 1.15))
            ax.set_ylim(0, ymax)
            ax.set_yticks(range(0, int(ymax) + 1, max(1, int(ymax // 5))))
            ax.tick_params(axis="x", rotation=45)
            self.figure.tight_layout()
            self.canvas.draw()


class RecipeParametersWidget(QWidget):
    """Widget for recipe-specific parameters (Lye, Water, Superfat)"""

    parameters_changed = pyqtSignal()
    master_batch_changed = pyqtSignal(bool, float)  # enabled, concentration

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Lye Type
        lye_layout = QHBoxLayout()
        lye_layout.addWidget(QLabel("Lye Type:"))
        self.lye_combo = QComboBox()
        self.lye_combo.addItems(["NaOH", "KOH", "90% KOH"])
        self.lye_combo.currentTextChanged.connect(self.on_lye_type_changed)
        lye_layout.addWidget(self.lye_combo)
        layout.addLayout(lye_layout)

        # Master Batch Lye Option
        from PyQt6.QtWidgets import QCheckBox

        mb_layout = QHBoxLayout()
        self.mb_check = QCheckBox("Use Master Batch Lye")
        self.mb_check.toggled.connect(self.on_mb_changed)
        mb_layout.addWidget(self.mb_check)

        self.mb_conc_spin = QDoubleSpinBox()
        self.mb_conc_spin.setRange(1, 99)
        self.mb_conc_spin.setValue(50.0)
        self.mb_conc_spin.setSuffix("% Conc")
        self.mb_conc_spin.setToolTip("Concentration of your pre-mixed lye solution")
        self.mb_conc_spin.valueChanged.connect(self.on_mb_changed)
        self.mb_conc_spin.setVisible(False)  # Hidden by default
        mb_layout.addWidget(self.mb_conc_spin)
        layout.addLayout(mb_layout)

        # Superfat
        superfat_layout = QHBoxLayout()
        superfat_layout.addWidget(QLabel("Superfat %:"))
        self.superfat_spinbox = QDoubleSpinBox()
        self.superfat_spinbox.setRange(0, 25)
        self.superfat_spinbox.setValue(5)
        self.superfat_spinbox.setSingleStep(0.5)
        self.superfat_spinbox.valueChanged.connect(self.on_superfat_changed)
        superfat_layout.addWidget(self.superfat_spinbox)
        layout.addLayout(superfat_layout)

        # Water Calculation Method
        water_method_layout = QHBoxLayout()
        water_method_layout.addWidget(QLabel("Water Calculation:"))
        self.water_method_combo = QComboBox()
        self.water_method_combo.addItems(
            ["Water:Lye Ratio", "Water % of Oils", "Lye Concentration"]
        )
        self.water_method_combo.currentTextChanged.connect(self.on_water_method_changed)
        water_method_layout.addWidget(self.water_method_combo)
        layout.addLayout(water_method_layout)

        # Water calculation value (dynamic based on method)
        self.water_value_layout = QHBoxLayout()
        self.water_value_label = QLabel("Ratio:")
        self.water_value_layout.addWidget(self.water_value_label)
        self.water_value_spinbox = QDoubleSpinBox()
        self.water_value_spinbox.setRange(0.5, 5)
        self.water_value_spinbox.setValue(2.0)
        self.water_value_spinbox.setSingleStep(0.1)
        self.water_value_spinbox.valueChanged.connect(self.on_water_value_changed)
        self.water_value_layout.addWidget(self.water_value_spinbox)
        layout.addLayout(self.water_value_layout)

        self.setLayout(layout)

    def on_lye_type_changed(self, lye_type: str):
        self.calculator.set_lye_type(lye_type)
        self.parameters_changed.emit()

    def on_superfat_changed(self):
        self.calculator.set_superfat(self.superfat_spinbox.value())
        self.parameters_changed.emit()

    def on_water_method_changed(self, method_text: str):
        method_map = {
            "Water:Lye Ratio": "ratio",
            "Water % of Oils": "percent",
            "Lye Concentration": "concentration",
        }
        method = method_map.get(method_text, "ratio")
        self.calculator.set_water_calc_method(method)

        # Update label and spinbox settings based on method
        if method == "ratio":
            self.water_value_label.setText("Ratio:")
            self.water_value_spinbox.setRange(0.5, 5)
            self.water_value_spinbox.setValue(self.calculator.water_to_lye_ratio)
        elif method == "percent":
            self.water_value_label.setText("% of Oils:")
            self.water_value_spinbox.setRange(0, 100)
            self.water_value_spinbox.setValue(self.calculator.water_percent)
        elif method == "concentration":
            self.water_value_label.setText("Lye % (concentration):")
            self.water_value_spinbox.setRange(1, 99)
            self.water_value_spinbox.setValue(self.calculator.lye_concentration)

        self.parameters_changed.emit()

    def on_water_value_changed(self):
        value = self.water_value_spinbox.value()
        self.calculator.set_water_calc_method(self.calculator.water_calc_method, value)
        self.parameters_changed.emit()

    def on_mb_changed(self):
        enabled = self.mb_check.isChecked()
        self.mb_conc_spin.setVisible(enabled)
        self.master_batch_changed.emit(enabled, self.mb_conc_spin.value())


class SettingsWidget(QWidget):
    """Widget for recipe settings"""

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
        unit_map = {"Grams": "grams", "Ounces": "ounces", "Pounds": "pounds"}
        self.calculator.set_unit_system(unit_map.get(unit_text, "grams"))
        self.settings_changed.emit()

    def on_theme_changed(self, theme_text: str):
        """Handle theme accent change"""
        self.settings_changed.emit()

    def save_company_info(self):
        settings = QSettings("FireAndIceApothecary", "SoapCalc")
        settings.setValue("company_name", self.company_name.text())
        settings.setValue("company_website", self.website.text())


class RecipeManagementWidget(QWidget):
    """Widget for managing saved recipes"""

    def __init__(self, recipe_manager: RecipeManager, parent=None):
        super().__init__()
        self.recipe_manager = recipe_manager
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        """Setup recipe management controls"""
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Saved Recipes:"))

        # Recipes table
        self.recipes_table = QTableWidget()
        self.recipes_table.setColumnCount(2)
        self.recipes_table.setHorizontalHeaderLabels(["Recipe Name", "File"])
        self.recipes_table.setColumnWidth(0, 250)
        self.recipes_table.setColumnWidth(1, 300)
        layout.addWidget(self.recipes_table)

        # Buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_recipe_list)
        button_layout.addWidget(refresh_btn)
        load_btn = QPushButton("Load Selected")
        load_btn.clicked.connect(self.load_selected)
        button_layout.addWidget(load_btn)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.refresh_recipe_list()

    def refresh_recipe_list(self):
        """Refresh list of saved recipes"""
        recipes = self.recipe_manager.list_recipes()
        self.recipes_table.setRowCount(len(recipes))

        for row, (filename, name, filepath) in enumerate(recipes):
            self.recipes_table.setItem(row, 0, QTableWidgetItem(name))
            self.recipes_table.setItem(row, 1, QTableWidgetItem(str(filepath)))

    def load_selected(self):
        """Load selected recipe"""
        if self.recipes_table.currentRow() >= 0:
            filepath = self.recipes_table.item(
                self.recipes_table.currentRow(), 1
            ).text()
            if self.parent_window:
                self.parent_window.load_recipe_file(filepath)

    def delete_selected(self):
        """Delete selected recipe"""
        if self.recipes_table.currentRow() >= 0:
            filepath = self.recipes_table.item(
                self.recipes_table.currentRow(), 1
            ).text()
            if self.recipe_manager.delete_recipe(filepath):
                self.refresh_recipe_list()


class RecipeNotesWidget(QWidget):
    """Widget for recipe notes and instructions"""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Recipe Notes & Instructions:"))

        self.notes_area = QTextEdit()
        self.notes_area.setPlaceholderText(
            "Enter your process notes, temperature observations, and instructions here..."
        )
        layout.addWidget(self.notes_area)

        self.setLayout(layout)

    def get_notes(self) -> str:
        return self.notes_area.toPlainText()

    def set_notes(self, text: str):
        self.notes_area.setPlainText(text)


class RecipeReportWidget(QWidget):
    """Widget for viewing and printing the recipe"""

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Toolbar
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh View")
        refresh_btn.clicked.connect(lambda: self.refresh_report())
        btn_layout.addWidget(refresh_btn)

        if _HAS_PRINTER:
            print_btn = QPushButton("Print / Save PDF")
            print_btn.clicked.connect(self.print_report)
            btn_layout.addWidget(print_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Viewer
        self.viewer = QTextBrowser()
        layout.addWidget(self.viewer)

        self.setLayout(layout)

    def refresh_report(self, recipe_name="Current Recipe", notes=""):
        """Generate HTML report"""
        props = self.calculator.get_batch_properties()
        unit = self.calculator.unit_system
        unit_abbr = self.calculator.get_unit_abbreviation()
        qualities = props.get("relative_qualities", {})
        fa_profile = props.get("fa_breakdown", {})

        label_html = self.generate_label_html(props)

        # Define ranges for qualities
        quality_ranges = [
            ("Hardness", 29, 54),
            ("Cleansing", 12, 22),
            ("Conditioning", 44, 69),
            ("Bubbly", 14, 46),
            ("Creamy", 16, 48),
            ("Iodine", 41, 70),
            ("INS", 136, 165),
        ]

        # Helper to format weight
        def fmt(w):
            return f"{self.calculator.convert_weight(w, unit):.2f}"

        # Get Company Info
        settings = QSettings("FireAndIceApothecary", "SoapCalc")
        company_name = settings.value("company_name", "")
        website = settings.value("company_website", "")

        # Date
        date_str = datetime.now().strftime("%Y-%m-%d")

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; background-color: #fff; font-size: 11px; }}

                /* Letterhead Styles */
                .header-table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; border-bottom: 2px solid #1565c0; padding-bottom: 10px; }}
                .company-name {{ font-size: 22px; font-weight: bold; color: #1565c0; margin: 0; }}
                .company-web {{ font-size: 12px; color: #666; margin-top: 4px; }}
                .report-title {{ font-size: 18px; font-weight: bold; color: #333; text-align: right; }}
                .report-date {{ font-size: 11px; color: #888; text-align: right; margin-top: 4px; }}

                .section-header {{
                    background-color: #e3f2fd;
                    color: #0d47a1;
                    padding: 4px 8px;
                    font-weight: bold;
                    font-size: 1.0em;
                    margin-top: 10px;
                    border-left: 4px solid #1565c0;
                }}

                table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
                th {{ text-align: right; background-color: #f5f5f5; padding: 4px; border: 1px solid #e0e0e0; color: #424242; font-weight: bold; }}
                th.left-align {{ text-align: left; }}
                td {{ padding: 4px; border: 1px solid #f0f0f0; text-align: right; }}
                td.left-align {{ text-align: left; }}

                .param-table td {{ border: none; text-align: left; padding: 2px; }}
                .param-label {{ font-weight: bold; width: 160px; }}

                .highlight {{ font-weight: bold; color: #0277bd; }}
                .notes-box {{ background-color: #fffde7; padding: 8px; border: 1px solid #fff9c4; margin-top: 5px; white-space: pre-wrap; }}

                .out-of-range {{ color: #d32f2f; font-weight: bold; }}
                .in-range {{ color: #2e7d32; }}

                .bar-container {{ background-color: #f0f0f0; height: 12px; width: 100%; border-radius: 2px; }}
                .bar-fill {{ background-color: #1976d2; height: 100%; border-radius: 2px; }}
            </style>
        </head>
        <body>
            <!-- Letterhead Header -->
            <table class="header-table">
                <tr>
                    <td style="border:none; vertical-align: bottom;">
                        <div class="company-name">🌿 {company_name if company_name else "Fire & Ice Apothecary"}</div>
                        <div class="company-web">{website}</div>
                    </td>
                    <td style="border:none; vertical-align: bottom;">
                        <div class="report-title">{recipe_name}</div>
                        <div class="report-date">Date: {date_str}</div>
                    </td>
                </tr>
            </table>
        """

        # Calculate true total weight early for display
        additive_weight = sum(self.calculator.additives.values())
        true_total_weight = props["total_batch_weight"] + additive_weight

        html += f"""
            <!-- Top Section: Parameters and Totals Side-by-Side -->
            <table style="border:none; width:100%; margin-top:0;">
            <tr style="vertical-align:top;">
            <td style="width:48%; border:none; padding:0; padding-right:10px;">
                <div class="section-header" style="margin-top:0;">Batch Parameters</div>
                <table class="param-table">
                    <tr><td class="param-label">Total Oil Weight:</td><td>{self.calculator.convert_weight(props['total_oil_weight'], 'pounds'):.2f} lbs / {props['total_oil_weight']:.0f} g</td></tr>
                    <tr><td class="param-label">Water % of Oils:</td><td>{(props['water_weight'] / props['total_oil_weight'] * 100) if props['total_oil_weight'] else 0:.1f} %</td></tr>
                    <tr><td class="param-label">Super Fat:</td><td>{self.calculator.superfat_percent} %</td></tr>
                    <tr><td class="param-label">Lye Concentration:</td><td>{(props['lye_weight'] / (props['lye_weight'] + props['water_weight']) * 100) if (props['lye_weight'] + props['water_weight']) else 0:.1f} %</td></tr>
                    <tr><td class="param-label">Water : Lye Ratio:</td><td>{(props['water_weight'] / props['lye_weight']) if props['lye_weight'] else 0:.2f}:1</td></tr>
                    <tr><td class="param-label">Lye Type:</td><td>{self.calculator.lye_type}</td></tr>
                </table>
            </td>
            <td style="width:48%; border:none; padding:0;">
                <div class="section-header" style="margin-top:0;">Liquids & Totals</div>
                <table>
                    <tr><th class="left-align">Item</th><th>Pounds</th><th>Ounces</th><th>Grams</th></tr>
                    <tr><td class="left-align">Water</td><td>{props['water_weight']/453.592:.2f}</td><td>{props['water_weight']/28.3495:.2f}</td><td>{props['water_weight']:.1f}</td></tr>
                    <tr><td class="left-align">Lye</td><td>{props['lye_weight']/453.592:.2f}</td><td>{props['lye_weight']/28.3495:.2f}</td><td>{props['lye_weight']:.1f}</td></tr>
                    <tr style="font-weight:bold;"><td class="left-align">Total Batch</td><td>{true_total_weight/453.592:.2f}</td><td>{true_total_weight/28.3495:.2f}</td><td>{true_total_weight:.1f}</td></tr>
                </table>
            </td>
            </tr>
            </table>

            <div class="section-header">Oils & Ingredients</div>
            <table>
                <tr><th class="left-align">Oil Name</th><th>%</th><th>Pounds</th><th>Ounces</th><th>Grams</th></tr>
        """

        total_oil = props["total_oil_weight"]
        for name, weight in self.calculator.oils.items():
            pct = (weight / total_oil * 100) if total_oil > 0 else 0
            html += f"<tr><td class='left-align'>{name}</td><td>{pct:.1f}</td><td>{weight/453.592:.3f}</td><td>{weight/28.3495:.2f}</td><td>{weight:.2f}</td></tr>"

        html += f"""
                <tr style="font-weight:bold; background-color:#fafafa;"><td class="left-align">Totals</td><td>100.0</td><td>{total_oil/453.592:.3f}</td><td>{total_oil/28.3495:.2f}</td><td>{total_oil:.2f}</td></tr>
            </table>
        """

        if self.calculator.additives:
            html += """
            <div class="section-header">Additives</div>
            <table>
                <tr><th class="left-align">Additive</th><th>Pounds</th><th>Ounces</th><th>Grams</th></tr>
            """
            for name, weight in self.calculator.additives.items():
                html += f"<tr><td class='left-align'>{name}</td><td>{weight/453.592:.3f}</td><td>{weight/28.3495:.2f}</td><td>{weight:.2f}</td></tr>"
            html += "</table>"

        # Two-column layout for Qualities and FA
        html += """
        <table style="border: none; margin-top: 20px;">
            <tr style="vertical-align: top;">
                <td style="width: 48%; border: none; padding: 0; padding-right: 10px;">
                    <div class="section-header" style="margin-top: 0;">Soap Qualities</div>
                    <table>
                        <tr><th class="left-align">Quality</th><th>Range</th><th>Value</th></tr>
        """

        for name, min_val, max_val in quality_ranges:
            val = int(round(qualities.get(name.lower(), 0)))
            style_class = (
                "out-of-range" if (val < min_val or val > max_val) else "in-range"
            )
            html += f"<tr><td class='left-align'>{name}</td><td>{min_val} - {max_val}</td><td class='{style_class}'>{val}</td></tr>"

        html += """
                    </table>
                </td>
                <td style="width: 4%; border: none;"></td>
                <td style="width: 48%; border: none; padding: 0;">
                    <div class="section-header" style="margin-top: 0;">Fatty Acid Profile</div>
                    <table>
                        <tr><th class="left-align">Acid</th><th>%</th></tr>
        """

        fa_order = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "ricinoleic",
            "oleic",
            "linoleic",
            "linolenic",
        ]
        for fa in fa_order:
            val = float(fa_profile.get(fa, 0.0))
            if val > 0.1:  # Only show present FAs
                html += f"""
                <tr>
                    <td class='left-align'>{fa.capitalize()}</td>
                    <td>{val:.1f}%</td>
                </tr>
                """

        html += """
                    </table>
                </td>
            </tr>
        </table>
        """

        html += label_html

        if notes:
            html += f"<div class='section-header'>Instructions & Notes</div><div class='notes-box'>{notes}</div>"

        html += "</body></html>"
        self.viewer.setHtml(html)

    def generate_label_html(self, props):
        """Generate INCI label preview"""
        # Determine salt prefix based on lye
        lye_type = self.calculator.lye_type
        prefix = "Potassium" if "KOH" in lye_type else "Sodium"

        # Common INCI root mapping
        # This maps the oil name to the root used with Sodium/Potassium
        inci_roots = {
            "Olive Oil": "Olivate",
            "Coconut Oil": "Cocoate",
            "Palm Oil": "Palmate",
            "Castor Oil": "Castorate",
            "Sweet Almond Oil": "Sweet Almondate",
            "Avocado Oil": "Avocadoate",
            "Shea Butter": "Shea Butterate",
            "Cocoa Butter": "Cocoa Butterate",
            "Lard": "Lardate",
            "Tallow": "Tallowate",
            "Babassu Oil": "Babassuate",
            "Sunflower Oil": "Sunflowerate",
            "Safflower Oil": "Safflowerate",
            "Rice Bran Oil": "Rice Branate",
            "Mango Seed Butter": "Mango Butterate",
            "Hemp Oil": "Hempseedate",
            "Neem Seed Oil": "Neemate",
            "Stearic Acid": "Stearate",
        }

        # Collect all ingredients with weights
        ingredients = []

        # Oils (converted to salts)
        for name, weight in self.calculator.oils.items():
            # Check if we have a mapping
            root = inci_roots.get(name)
            if root:
                inci_name = f"{prefix} {root}"
            else:
                # Fallback for unmapped oils
                inci_name = f"Saponified {name}"
            ingredients.append((weight, inci_name))

        # Additives
        for name, weight in self.calculator.additives.items():
            # Simple mapping for common additives
            if "Fragrance" in name or "EO" in name:
                ingredients.append((weight, "Parfum (Fragrance)"))
            else:
                ingredients.append((weight, name))

        # Water (Aqua) and Glycerin
        # Note: In a finished bar, much water evaporates, but Glycerin is produced.
        # This is an estimation. Glycerin is roughly ~10% of oil weight in cold process.
        # Water remaining is variable, but we'll list Aqua based on input water for the raw list order,
        # or place it appropriately. Standard INCI lists Aqua often 1st or 2nd.
        # For simplicity in this generator, we will add Aqua and Glycerin based on batch proportions.

        ingredients.append((props["water_weight"], "Aqua"))
        ingredients.append(
            (props["total_oil_weight"] * 0.1, "Glycerin")
        )  # Rough estimate

        # Sort by weight descending
        ingredients.sort(key=lambda x: x[0], reverse=True)

        # Format list
        label_text = ", ".join([item[1] for item in ingredients])

        return f"""
        <div class="section-header">Ingredient Label (INCI Preview)</div>
        <div style="padding: 8px; border: 1px dashed #999; background-color: #f9f9f9; margin-top: 5px; font-size: 10px;">
            <b>Ingredients:</b> {label_text}
        </div>
        <div style="font-size: 11px; color: #666; margin-top: 5px;">* Generated estimation. Verify with local regulations.</div>
        """

    def print_report(self):
        if not _HAS_PRINTER:
            return

        # Use ScreenResolution to fix tiny text issue in PDFs
        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)

        preview = QPrintPreviewDialog(printer, self)
        preview.setMinimumSize(1000, 800)
        preview.paintRequested.connect(lambda p: self.viewer.print(p))
        preview.exec()


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
        form.addRow("Packaging Cost ($/bar):", self.packaging_cost_spin)

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
