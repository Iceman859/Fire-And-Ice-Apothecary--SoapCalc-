"""Recipe Tab UI Components"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QTableWidget,
    QCompleter,
    QGroupBox,
    QGridLayout,
    QStackedWidget,
    QScrollArea,
    QSplitter,
    QCheckBox,
    QTextEdit,
)
from PyQt6.QtCore import pyqtSignal, Qt

# Data & Logic Imports
from src.data import get_all_oil_names
from src.data.additives import get_all_additive_names, get_additive_info, get_all_fragrance_names
from src.ui.skincare_ingredients import is_exfoliant as check_is_exfoliant
from src.models import SoapCalculator


class OilInputWidget(QWidget):
    """Widget for adding oils to recipe"""

    oil_added = pyqtSignal()

    def __init__(
        self,
        calculator: SoapCalculator,
        mode: str = "soap",
        ingredient_names: list = None,
        add_method_name: str = "add_oil",
        cost_manager=None,
        parent=None,
    ):
        super().__init__(parent)
        self.calculator = calculator
        self.target_weight_callback = None
        self.mode = mode
        self.ingredient_names = ingredient_names
        self.add_method_name = add_method_name
        self.cost_manager = cost_manager
        self.setup_ui()

    def setup_ui(self):
        """Setup oil input controls"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label_text = "Oil:" if self.mode == "soap" else "Ingredient:"
        # Oil selection
        self.input_label = QLabel(label_text)
        layout.addWidget(self.input_label)
        self.oil_combo = QComboBox()
        self.oil_combo.setEditable(True)
        self.refresh_oils()
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

    def add_oil(self):
        """Add selected oil to recipe"""
        oil_name = self.oil_combo.currentText()
        weight = self.weight_spinbox.value()
        unit = self.weight_unit_combo.currentText()

        if weight > 0:
            weight_grams = 0.0
            if unit == "%":
                if self.target_weight_callback:
                    # This will now get 32.0 from our new_recipe default
                    target_val = self.target_weight_callback()

                    # Convert that 32.0 oz to grams so the calculator stays happy
                    # (32 * 28.3495 = ~907g)
                    total_grams = self.calculator.convert_to_grams(target_val, "ounces")

                    weight_grams = total_grams * (weight / 100.0)
            else:
                unit_map = {"g": "grams", "oz": "ounces", "lbs": "pounds"}
                weight_grams = self.calculator.convert_to_grams(weight, unit_map[unit])

            if weight_grams > 0:
                add_method = getattr(self.calculator, self.add_method_name)
                add_method(oil_name, weight_grams)
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
        """Refresh the oil list from database and inventory."""
        current = self.oil_combo.currentText()
        self.oil_combo.clear()

        if self.ingredient_names:
            names = self.ingredient_names[:]
        else:
            names = get_all_oil_names()

        if self.cost_manager:
            inventory_items = sorted(self.cost_manager.costs.keys())
            names = sorted(list(set(names + inventory_items)))

        self.oil_combo.addItems(names)
        self.oil_combo.setCurrentText(current)

        completer = QCompleter(names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.oil_combo.setCompleter(completer)

    def set_mode(self, mode: str):
        """Update widget mode (label text)"""
        self.mode = mode
        if self.mode == "soap":
            self.input_label.setText("Oil:")
        else:
            self.input_label.setText("Ingredient:")

    def get_oils(self):
        """Returns the current oils in the calculator brain."""
    # Since the calculator brain is shared, we can just return
    # the oils currently stored in the calculator it was initialized with.
        return self.calculator.oils

class AdditiveInputWidget(QWidget):
    """Widget for adding recipe additives"""

    additive_added = pyqtSignal()

    def __init__(self, calculator: SoapCalculator, cost_manager=None, parent=None):
        super().__init__(parent)
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.setup_ui()

    def setup_ui(self):
        self.group = QGroupBox("Additives", self)
        layout = QGridLayout(self.group)

        layout.addWidget(QLabel("Additive:"), 0, 0)
        self.add_combo = QComboBox()
        self.add_combo.setEditable(True)

        additive_names = get_all_additive_names()
        if self.cost_manager:
            inventory_items = sorted(self.cost_manager.costs.keys())
            additive_names = sorted(list(set(additive_names + inventory_items)))

        self.add_combo.addItems(additive_names)
        self.add_combo.setCurrentIndex(-1)
        completer = QCompleter(additive_names)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.add_combo.setCompleter(completer)
        layout.addWidget(self.add_combo, 0, 1)

        layout.addWidget(QLabel("Mode:"), 1, 0)
        self.amount_type_combo = QComboBox()
        self.amount_type_combo.addItems(["% of Oils", "Weight / Volume"])
        self.amount_type_combo.currentTextChanged.connect(self.on_amount_type_changed)
        layout.addWidget(self.amount_type_combo, 1, 1)

        layout.addWidget(QLabel("Amount:"), 2, 0)

        self.percent_widget = QWidget()
        p_layout = QHBoxLayout(self.percent_widget)
        p_layout.setContentsMargins(0, 0, 0, 0)
        self.add_spin = QDoubleSpinBox()
        self.add_spin.setRange(0, 100)
        self.add_spin.setSingleStep(0.5)
        self.add_spin.setValue(0)
        self.add_spin.setSuffix("%")
        p_layout.addWidget(self.add_spin)

        self.weight_widget = QWidget()
        w_layout = QHBoxLayout(self.weight_widget)
        w_layout.setContentsMargins(0, 0, 0, 0)
        self.add_weight_spin = QDoubleSpinBox()
        self.add_weight_spin.setRange(0, 10000)
        self.add_weight_spin.setSingleStep(1.0)
        self.add_weight_spin.setValue(0.0)
        w_layout.addWidget(self.add_weight_spin)
        self.add_unit_combo = QComboBox()
        self.add_unit_combo.addItems(["g", "oz", "lbs", "tsp", "tbsp"])
        self.add_unit_combo.setFixedWidth(60)
        w_layout.addWidget(self.add_unit_combo)

        layout.addWidget(self.percent_widget, 2, 1)
        layout.addWidget(self.weight_widget, 2, 1)
        self.weight_widget.setVisible(False)

        self.water_replace_check = QCheckBox("Replaces Water in Lye Solution?")
        layout.addWidget(self.water_replace_check, 3, 0, 1, 2)

        add_btn = QPushButton("Add Additive")
        add_btn.clicked.connect(self.add_additive)
        layout.addWidget(add_btn, 4, 0, 1, 2)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group)

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
            if unit == "tsp":
                amount_grams = val * 5.0
            elif unit == "tbsp":
                amount_grams = val * 15.0
            else:
                unit_map = {"g": "grams", "oz": "ounces", "lbs": "pounds"}
                amount_grams = self.calculator.convert_to_grams(val, unit_map[unit])

        if amount_grams > 0:
            self.calculator.add_additive(name, amount_grams)
            self.add_spin.setValue(0)
            self.add_weight_spin.setValue(0)
            self.additive_added.emit()

    def on_amount_type_changed(self, text: str):
        if text == "% of Oils":
            self.percent_widget.setVisible(True)
            self.weight_widget.setVisible(False)
        else:
            self.percent_widget.setVisible(False)
            self.weight_widget.setVisible(True)

    def set_mode(self, mode: str):
        is_soap = mode == "soap"
        self.group.setTitle("Additives & Water Replacement" if is_soap else "Additives")
        self.water_replace_check.setVisible(is_soap)

    def set_unit_system(self, unit_system: str):
        unit_map = {"grams": "g", "ounces": "oz", "pounds": "lbs"}
        self.add_unit_combo.setCurrentText(unit_map.get(unit_system, "g"))

    def refresh_additives(self):
        current = self.add_combo.currentText()
        self.add_combo.clear()
        names = get_all_additive_names()
        if self.cost_manager:
            inventory_items = sorted(self.cost_manager.costs.keys())
            names = sorted(list(set(names + inventory_items)))
        self.add_combo.addItems(names)
        self.add_combo.setCurrentText(current)


class FragranceWidget(QWidget):
    """Widget to calculate fragrance amount based on usage rate"""
    fragrance_added = pyqtSignal()

    def __init__(self, calculator: SoapCalculator, cost_manager=None, parent=None):
        super().__init__(parent)
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.setup_ui()

    def setup_ui(self):
        group = QGroupBox("Fragrance / Essential Oil Calculator", self)
        layout = QGridLayout(group)

        layout.addWidget(QLabel("Scent Name:"), 0, 0)
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        items = get_all_fragrance_names()
        self.name_combo.addItems(items)
        self.name_combo.setCurrentIndex(-1)
        layout.addWidget(self.name_combo, 0, 1)

        layout.addWidget(QLabel("Usage Rate:"), 1, 0)
        rate_layout = QHBoxLayout()
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 10)
        self.rate_spin.setValue(0.50)
        #probably wrong function for adding fragrance
        self.rate_spin.valueChanged.connect(self.update_calculation)

        rate_layout.addWidget(self.rate_spin)
        self.rate_unit_combo = QComboBox()
        self.rate_unit_combo.addItems(["%", "oz/lb", "g/kg"])
        self.rate_unit_combo.setCurrentText("oz/lb")
        rate_layout.addWidget(self.rate_unit_combo)
        layout.addLayout(rate_layout, 1, 1)

        layout.addWidget(QLabel("Required Amount:"), 2, 0)
        self.amount_lbl = QLabel("0.00 g")
        self.amount_lbl.setStyleSheet("font-weight: bold; color: #4fc3f7;")
        layout.addWidget(self.amount_lbl, 2, 1)

        add_btn = QPushButton("Add Fragrance")
        add_btn.clicked.connect(self.add_fragrance)
        layout.addWidget(add_btn, 3, 0, 1, 2)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)

    def update_calculation(self):
        rate = self.rate_spin.value()
        total_oil = self.calculator.get_total_oil_weight()
        # simplified for brevity
        amount_grams = total_oil * (rate / 100.0)
        unit = self.calculator.unit_system
        display_amount = self.calculator.convert_weight(amount_grams, unit)
        self.amount_lbl.setText(
            f"{display_amount:.2f} {self.calculator.get_unit_abbreviation()}"
        )

    def add_fragrance(self):
            """Calculates fragrance amount in base units (grams) and adds to the recipe"""
            scent_name = self.name_combo.currentText()
            if not scent_name:
                # Optionally: self.show_error("Please select or enter a scent name")
                return

            usage_rate = self.rate_spin.value()
            unit_type = self.rate_unit_combo.currentText()

            # We assume get_total_oil_weight() returns the base mass in Grams
            total_oil_base = self.calculator.get_total_oil_weight()

            if total_oil_base <= 0:
                return

            # --- CALCULATION LOGIC (RATIO BASED) ---
            # We calculate the amount in the same unit as total_oil_base (Grams)
            if unit_type == "%":
                # Ratio: Part per 100
                amount_base = (usage_rate / 100) * total_oil_base

            elif unit_type == "oz/lb":
                # Ratio: 1 part per 16 parts (Standard Fragrance Math)
                # This is mathematically identical to (usage_rate / 16) * total_oil
                amount_base = (usage_rate / 16) * total_oil_base

            elif unit_type == "g/kg":
                # Ratio: 1 part per 1000 parts
                amount_base = (usage_rate / 1000) * total_oil_base
            else:
                amount_base = 0

            # 4. Send the Base Grams to the calculator.
            self.calculator.add_additive(scent_name, amount_base)

            # 5. Trigger the UI refresh
            self.fragrance_added.emit()
            self.name_combo.setCurrentIndex(-1)

    def refresh_ingredients(self):
        pass


class CalculationResultsWidget(QWidget):
    """Widget for displaying calculation results"""

    packaging_cost_changed = pyqtSignal(float)

    def __init__(
        self,
        calculator: SoapCalculator = None,
        cost_manager=None,
        mode: str = "soap",
        parent=None,
    ):
        super().__init__(parent)
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.mode = mode
        self.last_properties = {}
        self.last_unit = "grams"
        self.last_name = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.recipe_name_label = QLabel("Unsaved Recipe")
        self.recipe_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.recipe_name_label.font()
        font.setBold(True)
        self.recipe_name_label.setFont(font)
        layout.addWidget(self.recipe_name_label)

        self.weights_group = QGroupBox("Batch Weights")
        w_layout = QGridLayout(self.weights_group)
        self.weight_labels = {}
        self.row_widgets = {}
        weight_keys = [
            "Total Oil Weight",
            "Water Weight",
            "Add'l Water",
            "Lye Weight",
            "Exfoliant:Oil Ratio",
            "Total Batch Weight",
            "Total Batch Cost",
        ]

        for i, key in enumerate(weight_keys):
            lbl = QLabel(f"{key}:")
            w_layout.addWidget(lbl, i, 0)
            val_lbl = QLabel("0.00")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            w_layout.addWidget(val_lbl, i, 1)
            self.weight_labels[key] = val_lbl
            self.row_widgets[key] = (lbl, val_lbl)

        layout.addWidget(self.weights_group)

        # Yield Estimation
        self.yield_group = QGroupBox("Yield Estimation")
        y_layout = QGridLayout(self.yield_group)
        self.bar_size_spin = QDoubleSpinBox()
        self.bar_size_spin.setRange(0.1, 5000)
        self.bar_size_spin.setValue(4.5)
        y_layout.addWidget(QLabel("Bar Size:"), 0, 0)
        y_layout.addWidget(self.bar_size_spin, 0, 1)
        self.ypacking_cost_spin = QDoubleSpinBox()
        self.ypacking_cost_spin.setRange(0, 100)
        y_layout.addWidget(QLabel("Packaging Cost:"), 1, 0)
        y_layout.addWidget(self.ypacking_cost_spin, 1, 1)
        self.yield_label = QLabel("0.0 units")
        y_layout.addWidget(QLabel("Est. Yield:"), 2, 0)
        y_layout.addWidget(self.yield_label, 2, 1)
        self.cost_per_unit_label = QLabel("$0.00")
        y_layout.addWidget(QLabel("Cost/Unit:"), 3, 0)
        y_layout.addWidget(self.cost_per_unit_label, 3, 1)
        layout.addWidget(self.yield_group)
        self.bar_size_spin.valueChanged.connect(lambda: self.update_display(self.last_properties))
        self.ypacking_cost_spin.valueChanged.connect(lambda: self.update_display(self.last_properties))
        self.ypacking_cost_spin.valueChanged.connect(self.on_packaging_cost_changed)


    def on_packaging_cost_changed(self, value):
        self.packaging_cost_changed.emit(value)

    def set_mode(self, mode: str):
        self.mode = mode

    def update_display(self, results):
            """Receives calculations and updates the labels on the screen."""

            if not results:
                return

    # CRITICAL: Save the results so the spinbox can use them later
            self.last_properties = results

            unit = results.get('unit_system', 'g').lower()
            if unit == "ounces": unit = "oz"
            if unit == "grams": unit = "g"

            # --- NEW MATH START ---
            # 1. Calculate Cost (Iterate through what's in the calculator)
            total_cost = 0.0
            if self.cost_manager and self.calculator:
                # Sum Oils
                for name, weight in self.calculator.oils.items():
                    total_cost += (weight * self.cost_manager.get_cost_per_gram(name))
                # Sum Additives
                for name, weight in self.calculator.additives.items():
                    total_cost += (weight * self.cost_manager.get_cost_per_gram(name))

            # 2. Calculate Yield
            total_weight = results.get('total_batch_weight', 0.0)
            container_size = self.bar_size_spin.value()
            est_yield = total_weight / container_size if container_size > 0 else 0.0

            # Inject these into the results so the mapping below finds them
            results['total_batch_cost'] = total_cost
            results['yield'] = est_yield
            # --- NEW MATH END ---

            # ... (Keep your existing mapping and loop below) ...
            mapping = {
                "Total Oil Weight": "total_oil_weight",
                "Water Weight": "water_weight",
                "Lye Weight": "lye_weight",
                "Total Batch Weight": "total_batch_weight",
                "Total Batch Cost": "total_batch_cost" # Now it will find the value!
            }

            for ui_label_text, data_key in mapping.items():
                if ui_label_text in self.weight_labels:
                    value = results.get(data_key, 0.0)
                    if "Cost" in ui_label_text:
                        self.weight_labels[ui_label_text].setText(f"${value:.2f}")
                    else:
                        self.weight_labels[ui_label_text].setText(f"{value:.2f} {unit}")

            # Update Yield Label
            self.yield_label.setText(f"{est_yield:.1f} units")

            # Update Cost Per Unit
            cost_per_unit = total_cost / est_yield if est_yield > 0 else 0.0
            self.cost_per_unit_label.setText(f"${cost_per_unit:.2f}")

    def update_units(self, unit_text):
        """Update the unit labels in the results display"""
        # This assumes you have labels for weight and cost
        # Adjust the attribute names (like self.weight_unit_label)
        # to match what you actually named them in your __init__
        if hasattr(self, 'weight_unit_label'):
            self.weight_unit_label.setText(unit_text)

        # If you want to update the 'per unit' label (e.g., $/oz)
        if hasattr(self, 'cost_per_unit_label'):
            self.cost_per_unit_label.setText(f"Cost per {unit_text}")


class RecipeParametersWidget(QWidget):
    """Widget for recipe-specific parameters (Lye, Water, Superfat)"""

    parameters_changed = pyqtSignal()

    def __init__(self, calculator: SoapCalculator, parent=None):
        super().__init__(parent)
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.lye_combo = QComboBox()
        self.lye_combo.addItems(["NaOH", "KOH", "90% KOH"])
        layout.addWidget(QLabel("Lye Type:"))
        layout.addWidget(self.lye_combo)

        self.superfat_spinbox = QDoubleSpinBox()
        self.superfat_spinbox.setRange(0, 25)
        self.superfat_spinbox.setValue(5)
        layout.addWidget(QLabel("Superfat %:"))
        layout.addWidget(self.superfat_spinbox)

        self.water_method_combo = QComboBox()
        self.water_method_combo.addItems(
            ["Water:Lye Ratio", "Water % of Oils", "Lye Concentration"]
        )
        layout.addWidget(QLabel("Water Calculation:"))
        layout.addWidget(self.water_method_combo)

        self.water_value_spinbox = QDoubleSpinBox()
        self.water_value_label = QLabel("Ratio:")
        layout.addWidget(self.water_value_label)
        layout.addWidget(self.water_value_spinbox)

    def on_lye_type_changed(self, lye_type: str):
        pass

    def on_superfat_changed(self):
        pass

    def on_water_method_changed(self, method_text: str):
        pass

    def on_water_value_changed(self):
        pass

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

class RecipeTab(QWidget):
    """Main tab for recipe creation and calculations"""
    def __init__(self, calculator, cost_manager, recipe_controller, parent=None):
        super().__init__(parent)
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.controller = recipe_controller
        self.notes_widget = RecipeNotesWidget()
        self.additives_section = AdditivesSection(self.calculator, self.cost_manager)
        self.setup_ui()

    def setup_ui(self):
            """Setup the main UI layout for the recipe tab"""
            # 1. Initialize the main layout properly
            self.main_layout = QVBoxLayout(self)

            # Header section
            header_layout = QHBoxLayout()
            header_layout.addWidget(QLabel("Product Type:"))
            self.product_type_combo = QComboBox()
            self.product_type_combo.addItems([
                "Soap (Cold Process)", "Body Butter", "Body Scrub",
                "Lotion / Cream", "Balm / Salve", "Other"
            ])
            header_layout.addWidget(self.product_type_combo)
            header_layout.addStretch()
            self.main_layout.addLayout(header_layout)

            self.splitter = QSplitter(Qt.Orientation.Horizontal)

            # COLUMN 1: Settings & Notes
            col1_scroll = QScrollArea()
            col1_scroll.setWidgetResizable(True)
            col1_container = QWidget()
            col1_vbox = QVBoxLayout(col1_container)

            self.recipe_settings = RecipeParametersWidget(self.calculator, parent=self)
            col1_vbox.addWidget(QLabel("<b>Recipe Parameters</b>"))
            col1_vbox.addWidget(self.recipe_settings)

            col1_vbox.addSpacing(20)
            col1_vbox.addWidget(QLabel("<b>Process Notes</b>"))
            col1_vbox.addWidget(self.notes_widget)

            col1_vbox.addStretch()
            col1_scroll.setWidget(col1_container)

            # COLUMN 2: Ingredients (Oils, Additives, Fragrance)
            col2_scroll = QScrollArea()
            col2_scroll.setWidgetResizable(True)
            col2_container = QWidget()
            col2_vbox = QVBoxLayout(col2_container)
            self.middle_stack = QStackedWidget()

            soap_page = QWidget()
            soap_layout = QVBoxLayout(soap_page)

            # Oil Input Section
            self.oil_input_widget = OilInputWidget(
                self.calculator,
                mode="soap",
                ingredient_names=get_all_oil_names(),
                cost_manager=self.cost_manager,
                parent=self,
            )
            soap_layout.addWidget(QLabel("<b>Add Ingredients:</b>"))
            soap_layout.addWidget(self.oil_input_widget)

            self.oils_table = QTableWidget()
            self.oils_table.setColumnCount(4)
            self.oils_table.setMinimumHeight(350)
            soap_layout.addWidget(self.oils_table)

            # --- THE SIDE-BY-SIDE SECTION ---
            soap_layout.addWidget(QLabel("<b>Additives & Fragrance:</b>"))

            # Create horizontal container
            input_row_layout = QHBoxLayout()
            input_row_layout.setSpacing(10)

            self.fragrance_widget = FragranceWidget(
                self.calculator, cost_manager=self.cost_manager, parent=self
            )
            self.additive_widget = AdditiveInputWidget(
                self.calculator, cost_manager=self.cost_manager, parent=self
            )

            # Add widgets to the horizontal row with equal stretch
            input_row_layout.addWidget(self.fragrance_widget, 1)
            input_row_layout.addWidget(self.additive_widget, 1)

            # Add the horizontal row to the soap layout
            soap_layout.addLayout(input_row_layout)

            # Additives Table (Below the inputs)
            self.additives_table = QTableWidget()
            self.additives_table.setColumnCount(6) # Updated to 6 for the Action/Remove column
            self.additives_table.setMinimumHeight(200)
            soap_layout.addWidget(self.additives_table)

            self.middle_stack.addWidget(soap_page)
            self.middle_stack.addWidget(QWidget()) # Placeholder

            col2_vbox.addWidget(self.middle_stack)
            col2_container.setLayout(col2_vbox)
            col2_scroll.setWidget(col2_container)

            # COLUMN 3: Results & Operations
            col3_scroll = QScrollArea()
            col3_scroll.setWidgetResizable(True)
            col3_container = QWidget()
            col3_vbox = QVBoxLayout(col3_container)

            self.results_widget = CalculationResultsWidget(
                self.calculator, cost_manager=self.cost_manager, mode="soap", parent=self
            )
            col3_vbox.addWidget(QLabel("<b>Calculation Results</b>"))
            col3_vbox.addWidget(self.results_widget)

            col3_vbox.addWidget(QLabel("<b>Scale Recipe:</b>"))
            self.scale_label = QLabel("Total Oil Weight (g):")
            col3_vbox.addWidget(self.scale_label)
            self.scale_spinbox = QDoubleSpinBox()
            self.scale_spinbox.setRange(0, 10000)
            col3_vbox.addWidget(self.scale_spinbox)

            self.scale_btn = QPushButton("Scale Recipe")
            col3_vbox.addWidget(self.scale_btn)

            col3_vbox.addWidget(QLabel("<b>Recipe Operations:</b>"))
            btn_layout = QHBoxLayout()
            self.new_btn = QPushButton("New")
            self.save_btn = QPushButton("Save")
            self.load_btn = QPushButton("Load")
            btn_layout.addWidget(self.new_btn)
            btn_layout.addWidget(self.save_btn)
            btn_layout.addWidget(self.load_btn)
            col3_vbox.addLayout(btn_layout)

            self.log_btn = QPushButton("Log Batch")
            self.log_btn.setStyleSheet("background-color: #e63eab; color: white;")
            col3_vbox.addWidget(self.log_btn)

            col3_vbox.addStretch()
            col3_scroll.setWidget(col3_container)

            # Final assembly
            self.splitter.addWidget(col1_scroll)
            self.splitter.addWidget(col2_scroll)
            self.splitter.addWidget(col3_scroll)
            self.main_layout.addWidget(self.splitter)

    def on_unit_changed(self, unit_text: str):
        # ... Keep this method at the end ...
            """Update the UI (The REACTION)"""
            print(f"DEBUG: RecipeTab RECEIVED unit change: {unit_text}")

            # 1. Update the scale label ("Total Oil Weight (g)" -> "(Ounces)")
            if hasattr(self, 'scale_label'):
                self.scale_label.setText(f"Total Oil Weight ({unit_text}):")

            if hasattr(self, 'scale_total_weight'):
                self.scale_total_weight.setText(f"Total Batch Weight ({unit_text}):")

            # 2. Sync the oil input unit selector so it matches the new setting
            if hasattr(self, 'oil_input_widget'):
                self.oil_input_widget.set_unit_system(unit_text.lower())

            # 3. Use the controller to trigger a full calculation and UI push
            # This is the "safe" way because your controller already knows
            # how to talk to both the calculator and the results_widget.
            if hasattr(self, 'controller'):
                self.controller.update_calculations()

            #Total Batch scale
            if hasattr(self, 'scale_total_weighgt'):
                self.scale_total_weight.setText(f"Total Batch Weight ({unit_text}):")

class AdditivesSection(QWidget):
    """A container that holds Fragrance and Additives side-by-side"""
    def __init__(self, calculator, cost_manager=None, parent=None):
        super().__init__(parent)
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.setup_ui()

    def setup_ui(self):
        # 1. Create the horizontal layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(15)

        # 2. Initialize the two specific widgets
        self.fragrance_calc = FragranceWidget(self.calculator, self.cost_manager)
        self.additives_input = AdditiveInputWidget(self.calculator, self.cost_manager)

        # 3. Add them to the layout with equal stretch (1, 1)
        self.main_layout.addWidget(self.fragrance_calc, 1)
        self.main_layout.addWidget(self.additives_input, 1)

    def refresh(self):
        """If you need them to 'talk', you can trigger updates here"""
        self.fragrance_calc.update_calculation()
        self.additives_input.refresh_additives()