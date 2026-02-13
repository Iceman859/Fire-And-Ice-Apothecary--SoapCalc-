"""UI Widgets"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QCompleter, QGroupBox,
    QGridLayout, QTextEdit, QTextBrowser
)
from PyQt6.QtCore import pyqtSignal, Qt
from src.models import SoapCalculator, RecipeManager
from src.data import get_all_oil_names
from src.data.additives import get_all_additive_names

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
    from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
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
        self.oil_combo.setCurrentIndex(-1) # Start blank
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
        self.add_combo.setCurrentIndex(-1) # Start blank
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
        p_layout.setContentsMargins(0,0,0,0)
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
        w_layout.setContentsMargins(0,0,0,0)
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


class FragranceWidget(QWidget):
    """Widget to calculate fragrance amount based on usage rate"""
    
    fragrance_added = pyqtSignal()

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        group = QGroupBox("Fragrance / Essential Oil Calculator")
        layout = QGridLayout()
        
        layout.addWidget(QLabel("Scent Name:"), 0, 0)
        self.name_combo = QComboBox()
        self.name_combo.setEditable(True)
        self.name_combo.addItems(["Lavender EO", "Peppermint EO", "Tea Tree EO", "Lemon EO", "Orange EO", "Fragrance Oil"])
        self.name_combo.setCurrentIndex(-1)
        self.name_combo.setPlaceholderText("e.g. Lavender EO")
        layout.addWidget(self.name_combo, 0, 1)
        
        layout.addWidget(QLabel("Usage Rate:"), 1, 0)
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setRange(0, 15) 
        self.rate_spin.setSingleStep(0.1)
        self.rate_spin.setValue(3.0) 
        self.rate_spin.setSuffix("%")
        self.rate_spin.setToolTip("Typical rates: EO (0.5-3%), FO (3-6%)")
        self.rate_spin.valueChanged.connect(self.update_calculation)
        layout.addWidget(self.rate_spin, 1, 1)
        
        layout.addWidget(QLabel("Required Amount:"), 2, 0)
        self.amount_lbl = QLabel("0.00 g")
        self.amount_lbl.setStyleSheet("font-weight: bold; color: #4fc3f7;")
        layout.addWidget(self.amount_lbl, 2, 1)
        
        add_btn = QPushButton("Add to Additives")
        add_btn.clicked.connect(self.add_fragrance)
        layout.addWidget(add_btn, 3, 0, 1, 2)
        
        group.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(group)
        self.setLayout(main_layout)
        
    def update_calculation(self):
        """Recalculate amount based on current total oils"""
        rate = self.rate_spin.value()
        total_oil = self.calculator.get_total_oil_weight()
        amount_grams = total_oil * (rate / 100.0)
        
        unit = self.calculator.unit_system
        display_amount = self.calculator.convert_weight(amount_grams, unit)
        abbr = self.calculator.get_unit_abbreviation()
        
        self.amount_lbl.setText(f"{display_amount:.2f} {abbr}")

    def add_fragrance(self):
        rate = self.rate_spin.value()
        total_oil = self.calculator.get_total_oil_weight()
        amount_grams = total_oil * (rate / 100.0)
        
        if amount_grams > 0:
            name = self.name_combo.currentText()
            if not name:
                name = "Fragrance"
            
            # Add to calculator additives
            self.calculator.add_additive(name, amount_grams)
            self.fragrance_added.emit()


class CalculationResultsWidget(QWidget):
    """Widget for displaying calculation results"""
    
    def __init__(self, calculator: SoapCalculator = None, cost_manager = None):
        super().__init__()
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Setup results display"""
        layout = QVBoxLayout()
        
        # Batch Weights
        self.weights_group = QGroupBox("Batch Weights")
        w_layout = QGridLayout()
        
        self.weight_labels = {}
        weight_keys = ["Total Oil Weight", "Water Weight", "Lye Weight", "Total Batch Weight", "Total Batch Cost"]
        
        for i, key in enumerate(weight_keys):
            w_layout.addWidget(QLabel(f"{key}:"), i, 0)
            val_lbl = QLabel("0.00")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            w_layout.addWidget(val_lbl, i, 1)
            self.weight_labels[key] = val_lbl
            
        self.weights_group.setLayout(w_layout)
        layout.addWidget(self.weights_group)
        
        # Predicted Qualities
        self.qualities_group = QGroupBox("Soap Bar Quality")
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
            ("INS", "136 - 165")
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
    
    def update_results(self, properties: dict, unit_system: str = "grams"):
        """Update displayed results"""
        unit_abbr = {
            "grams": "g",
            "ounces": "oz",
            "pounds": "lbs"
        }.get(unit_system, "g")
        
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
            lye_weight = properties.get('lye_weight', 0.0)
            lye_type = self.calculator.lye_type
            total_cost += lye_weight * self.cost_manager.get_cost_per_gram(lye_type)
        
        # Batch Weights
        weights_map = {
            "Total Oil Weight": properties['total_oil_weight'],
            "Water Weight": properties['water_weight'],
            "Lye Weight": properties['lye_weight'],
            "Total Batch Weight": properties['total_batch_weight'],
            "Total Batch Cost": total_cost
        }
        
        for key, val in weights_map.items():
            if key in self.weight_labels:
                if key == "Total Batch Cost":
                    self.weight_labels[key].setText(f"${float(val):.2f}")
                else:
                    self.weight_labels[key].setText(f"{convert_weight(val)} {unit_abbr}")
            
        # Soap Qualities
        qualities = properties.get('relative_qualities', {})
        
        quality_map = {
            "Hardness": qualities.get('hardness', 0),
            "Cleansing": qualities.get('cleansing', 0),
            "Conditioning": qualities.get('conditioning', 0),
            "Bubbly": qualities.get('bubbly', 0),
            "Creamy": qualities.get('creamy', 0),
            "Iodine": qualities.get('iodine', 0),
            "INS": qualities.get('ins', 0)
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
            'lauric', 'myristic', 'palmitic', 'stearic',
            'oleic', 'linoleic', 'linolenic', 'ricinoleic'
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
        fa = properties.get('fa_breakdown', {}) if properties else {}
        order = [
            'lauric', 'myristic', 'palmitic', 'stearic',
            'oleic', 'linoleic', 'linolenic', 'ricinoleic'
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
            ax.bar(labels, values, color='#0d47a1')
            ax.set_ylabel('%')
            ax.set_title('Fatty Acid Breakdown')
            # scale y-axis to percent range (0-100) with small padding
            max_val = max(values) if values else 0
            ymax = min(100, max(10, max_val * 1.15))
            ax.set_ylim(0, ymax)
            ax.set_yticks(range(0, int(ymax) + 1, max(1, int(ymax // 5))))
            ax.tick_params(axis='x', rotation=45)
            self.figure.tight_layout()
            self.canvas.draw()


class RecipeParametersWidget(QWidget):
    """Widget for recipe-specific parameters (Lye, Water, Superfat)"""
    
    parameters_changed = pyqtSignal()
    
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
        self.water_method_combo.addItems(["Water:Lye Ratio", "Water % of Oils", "Lye Concentration"])
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
            "Lye Concentration": "concentration"
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
        
        # Custom Ingredients Button
        custom_btn = QPushButton("Manage Custom Ingredients")
        custom_btn.clicked.connect(self.open_ingredient_editor)
        layout.addWidget(custom_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_unit_changed(self, unit_text: str):
        """Handle unit system change"""
        unit_map = {"Grams": "grams", "Ounces": "ounces", "Pounds": "pounds"}
        self.calculator.set_unit_system(unit_map.get(unit_text, "grams"))
        self.settings_changed.emit()

    def on_theme_changed(self, theme_text: str):
        """Handle theme accent change"""
        self.settings_changed.emit()
        
    def open_ingredient_editor(self):
        from src.ui.ingredient_editor import IngredientEditorDialog
        dialog = IngredientEditorDialog(self)
        dialog.exec()


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
            filepath = self.recipes_table.item(self.recipes_table.currentRow(), 1).text()
            if self.parent_window:
                self.parent_window.load_recipe_file(filepath)
    
    def delete_selected(self):
        """Delete selected recipe"""
        if self.recipes_table.currentRow() >= 0:
            filepath = self.recipes_table.item(self.recipes_table.currentRow(), 1).text()
            if self.recipe_manager.delete_recipe(filepath):
                self.refresh_recipe_list()


class RecipeNotesWidget(QWidget):
    """Widget for recipe notes and instructions"""
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Recipe Notes & Instructions:"))
        
        self.notes_area = QTextEdit()
        self.notes_area.setPlaceholderText("Enter your process notes, temperature observations, and instructions here...")
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
        
        # Helper to format weight
        def fmt(w):
            return f"{self.calculator.convert_weight(w, unit):.2f}"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; color: #000; background-color: #fff; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 20px; border-bottom: 1px solid #ddd; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
                th {{ text-align: left; background-color: #f2f2f2; padding: 8px; border-bottom: 1px solid #ddd; }}
                td {{ padding: 8px; border-bottom: 1px solid #eee; }}
                .highlight {{ font-weight: bold; color: #2980b9; }}
                .notes {{ background-color: #f9f9f9; padding: 15px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>{recipe_name}</h1>
            
            <h2>Batch Details</h2>
            <p>
                <b>Superfat:</b> {self.calculator.superfat_percent}% &nbsp;|&nbsp; 
                <b>Lye Type:</b> {self.calculator.lye_type} &nbsp;|&nbsp; 
                <b>Water Method:</b> {self.calculator.water_calc_method}
            </p>
            
            <h2>Oils</h2>
            <table>
                <tr><th>Oil Name</th><th>Weight ({unit_abbr})</th><th>%</th></tr>
        """
        
        total_oil = props['total_oil_weight']
        for name, weight in self.calculator.oils.items():
            pct = (weight / total_oil * 100) if total_oil > 0 else 0
            html += f"<tr><td>{name}</td><td>{fmt(weight)}</td><td>{pct:.1f}%</td></tr>"
            
        html += f"""
            </table>
            
            <h2>Lye & Liquids</h2>
            <table>
                <tr><td><b>Water / Liquid Amount:</b></td><td class="highlight">{fmt(props['water_weight'])} {unit_abbr}</td></tr>
                <tr><td><b>Lye Amount:</b></td><td class="highlight">{fmt(props['lye_weight'])} {unit_abbr}</td></tr>
                <tr><td><b>Total Batch Weight:</b></td><td>{fmt(props['total_batch_weight'])} {unit_abbr}</td></tr>
            </table>
        """
        
        if self.calculator.additives:
            html += "<h2>Additives</h2><table><tr><th>Additive</th><th>Amount</th></tr>"
            for name, weight in self.calculator.additives.items():
                html += f"<tr><td>{name}</td><td>{fmt(weight)} {unit_abbr}</td></tr>"
            html += "</table>"
            
        if notes:
            html += f"<h2>Instructions & Notes</h2><div class='notes'><pre>{notes}</pre></div>"
            
        html += "</body></html>"
        self.viewer.setHtml(html)

    def print_report(self):
        if not _HAS_PRINTER:
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.viewer.print(printer)


class InventoryCostWidget(QWidget):
    """Widget for managing ingredient costs"""
    
    def __init__(self, cost_manager):
        super().__init__()
        self.cost_manager = cost_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Input Form Group
        form_group = QGroupBox("Update Ingredient Cost")
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("Ingredient:"), 0, 0)
        self.ingredient_combo = QComboBox()
        self.ingredient_combo.setEditable(True)
        # Populate with oils and additives
        items = sorted(get_all_oil_names() + get_all_additive_names() + ["NaOH", "KOH", "90% KOH"])
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
        self.unit_combo.addItems(["grams", "oz", "lbs", "kg", "liters", "gallons", "fl oz"])
        form_layout.addWidget(self.unit_combo, 3, 1)
        
        save_btn = QPushButton("Save Cost")
        save_btn.clicked.connect(self.save_cost)
        form_layout.addWidget(save_btn, 4, 0, 1, 2)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Table
        self.cost_table = QTableWidget()
        self.cost_table.setColumnCount(4)
        self.cost_table.setHorizontalHeaderLabels(["Ingredient", "Price", "Quantity", "Cost/g"])
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
            
    def refresh_table(self):
        self.cost_table.setRowCount(0)
        costs = self.cost_manager.costs
        self.cost_table.setRowCount(len(costs))
        
        for i, (name, data) in enumerate(sorted(costs.items())):
            price = data.get('price', 0.0)
            qty = data.get('quantity', 0.0)
            unit = data.get('unit', '')
            cost_per_g = self.cost_manager.get_cost_per_gram(name)
            
            self.cost_table.setItem(i, 0, QTableWidgetItem(name))
            self.cost_table.setItem(i, 1, QTableWidgetItem(f"${price:.2f}"))
            self.cost_table.setItem(i, 2, QTableWidgetItem(f"{qty} {unit}"))
            self.cost_table.setItem(i, 3, QTableWidgetItem(f"${cost_per_g:.4f}"))
