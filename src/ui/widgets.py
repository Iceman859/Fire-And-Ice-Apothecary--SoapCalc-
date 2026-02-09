"""UI Widgets"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QCompleter
)
from PyQt6.QtCore import pyqtSignal
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


class OilInputWidget(QWidget):
    """Widget for adding oils to recipe"""
    
    oil_added = pyqtSignal()
    
    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()
    
    def setup_ui(self):
        """Setup oil input controls"""
        layout = QVBoxLayout()
        
        # Oil selection
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Oil:"))
        self.oil_combo = QComboBox()
        self.oil_combo.setEditable(True)
        names = get_all_oil_names()
        self.oil_combo.addItems(names)
        # simple completion
        completer = QCompleter(names)
        self.oil_combo.setCompleter(completer)
        select_layout.addWidget(self.oil_combo)
        layout.addLayout(select_layout)
        
        # Weight input with unit selector
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("Weight:"))
        self.weight_spinbox = QDoubleSpinBox()
        self.weight_spinbox.setRange(0, 10000)
        self.weight_spinbox.setValue(100)
        weight_layout.addWidget(self.weight_spinbox)
        
        self.weight_unit_combo = QComboBox()
        self.weight_unit_combo.addItems(["g", "oz", "lbs"])
        weight_layout.addWidget(self.weight_unit_combo)
        layout.addLayout(weight_layout)
        
        # Add button
        add_btn = QPushButton("Add Oil to Recipe")
        add_btn.clicked.connect(self.add_oil)
        layout.addWidget(add_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def add_oil(self):
        """Add selected oil to recipe"""
        oil_name = self.oil_combo.currentText()
        weight = self.weight_spinbox.value()
        unit = self.weight_unit_combo.currentText()
        
        if weight > 0:
            # Convert to grams for storage
            unit_map = {"g": "grams", "oz": "ounces", "lbs": "pounds"}
            weight_grams = self.calculator.convert_to_grams(weight, unit_map[unit])
            self.calculator.add_oil(oil_name, weight_grams)
            self.weight_spinbox.setValue(100)
            self.oil_added.emit()


class AdditiveInputWidget(QWidget):
    """Widget for adding recipe additives"""

    additive_added = pyqtSignal()

    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Additive:"))
        self.add_combo = QComboBox()
        self.add_combo.setEditable(True)
        self.add_combo.addItems(get_all_additive_names())
        select_layout.addWidget(self.add_combo)
        layout.addLayout(select_layout)

        # Amount type selector: percent of oils or explicit weight
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Amount Type:"))
        self.amount_type_combo = QComboBox()
        self.amount_type_combo.addItems(["% of Oils", "Weight"])
        self.amount_type_combo.currentTextChanged.connect(self.on_amount_type_changed)
        type_layout.addWidget(self.amount_type_combo)
        layout.addLayout(type_layout)

        # Percent input (default)
        self.percent_layout = QHBoxLayout()
        self.percent_layout.addWidget(QLabel("Amount (% of oils):"))
        self.add_spin = QDoubleSpinBox()
        self.add_spin.setRange(0, 100)
        self.add_spin.setSingleStep(0.5)
        self.add_spin.setValue(3.0)
        self.percent_layout.addWidget(self.add_spin)
        layout.addLayout(self.percent_layout)

        # Weight input (hidden by default)
        self.weight_layout = QHBoxLayout()
        self.weight_layout.addWidget(QLabel("Amount:"))
        self.add_weight_spin = QDoubleSpinBox()
        self.add_weight_spin.setRange(0, 10000)
        self.add_weight_spin.setSingleStep(1.0)
        self.add_weight_spin.setValue(50.0)
        self.weight_layout.addWidget(self.add_weight_spin)
        self.add_unit_combo = QComboBox()
        self.add_unit_combo.addItems(["g", "oz", "lbs"])
        self.weight_layout.addWidget(self.add_unit_combo)
        self.weight_widget = QWidget()
        self.weight_widget.setLayout(self.weight_layout)
        self.weight_widget.setVisible(False)
        layout.addWidget(self.weight_widget)

        add_btn = QPushButton("Add Additive")
        add_btn.clicked.connect(self.add_additive)
        layout.addWidget(add_btn)

        layout.addStretch()
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
            self.add_spin.setValue(3.0)
            self.add_weight_spin.setValue(50.0)
            self.additive_added.emit()

    def on_amount_type_changed(self, text: str):
        """Show/hide percent vs weight inputs"""
        if text == "% of Oils":
            self.percent_layout.parentWidget().setVisible(True) if hasattr(self.percent_layout, 'parentWidget') else None
            self.weight_widget.setVisible(False)
        else:
            # hide percent, show weight
            # percent layout was added directly to main layout; hide its widgets
            for i in range(self.percent_layout.count()):
                self.percent_layout.itemAt(i).widget().setVisible(False)
            self.weight_widget.setVisible(True)


class CalculationResultsWidget(QWidget):
    """Widget for displaying calculation results"""
    
    def __init__(self, calculator: SoapCalculator = None):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()
    
    def setup_ui(self):
        """Setup results display"""
        layout = QVBoxLayout()
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.results_table.setColumnWidth(0, 200)
        self.results_table.setColumnWidth(1, 150)
        layout.addWidget(self.results_table)
        
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
        
        rows = [
            ("Total Oil Weight", f"{convert_weight(properties['total_oil_weight'])} {unit_abbr}"),
            ("Lye Weight", f"{convert_weight(properties['lye_weight'])} {unit_abbr}"),
            ("Water Weight", f"{convert_weight(properties['water_weight'])} {unit_abbr}"),
            ("Total Batch Weight", f"{convert_weight(properties['total_batch_weight'])} {unit_abbr}"),
            ("Lye %", f"{properties['lye_percentage']:.2f}%"),
            ("Water %", f"{properties['water_percentage']:.2f}%"),
            ("Iodine Value", f"{properties['iodine_value']:.2f}"),
            ("INS Value", f"{properties['ins_value']:.2f}"),
        ]
        
        self.results_table.setRowCount(len(rows))
        for row, (name, value) in enumerate(rows):
            self.results_table.setItem(row, 0, QTableWidgetItem(name))
            self.results_table.setItem(row, 1, QTableWidgetItem(value))


class FABreakdownWidget(QWidget):
    """Displays fatty-acid breakdown as table and chart"""

    def __init__(self, calculator: SoapCalculator = None):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        # Two-column layout: left = table, right = chart
        layout = QHBoxLayout()

        # Table for FA breakdown (left column)
        self.fa_table = QTableWidget()
        self.fa_table.setColumnCount(2)
        self.fa_table.setHorizontalHeaderLabels(["Fatty Acid", "% of Total"])
        self.fa_table.setColumnWidth(0, 140)
        self.fa_table.setColumnWidth(1, 80)
        layout.addWidget(self.fa_table, 1)

        # Chart area (matplotlib) if available (right column)
        right_col = QVBoxLayout()
        if _HAS_MATPLOTLIB:
            self.figure = Figure(figsize=(4, 3))
            self.canvas = FigureCanvas(self.figure)
            right_col.addWidget(self.canvas)
        else:
            right_col.addWidget(QLabel("Install matplotlib to see chart."))

        layout.addLayout(right_col, 1)
        self.setLayout(layout)

    def update_fa(self, properties: dict, unit_system: str = "grams"):
        """Update FA breakdown table and chart from properties dict"""
        fa = properties.get('fa_breakdown', {}) if properties else {}
        order = [
            'lauric', 'myristic', 'palmitic', 'stearic',
            'oleic', 'linoleic', 'linolenic', 'ricinoleic'
        ]

        rows = len(order)
        self.fa_table.setRowCount(rows)
        values = []
        labels = []
        for i, key in enumerate(order):
            # `fa` provided by calculator is already percent (0-100)
            val = float(fa.get(key, 0.0))
            labels.append(key.capitalize())
            values.append(val)
            self.fa_table.setItem(i, 0, QTableWidgetItem(key.capitalize()))
            self.fa_table.setItem(i, 1, QTableWidgetItem(f"{val:.2f}%"))

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
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_unit_changed(self, unit_text: str):
        """Handle unit system change"""
        unit_map = {"Grams": "grams", "Ounces": "ounces", "Pounds": "pounds"}
        self.calculator.set_unit_system(unit_map.get(unit_text, "grams"))
        self.settings_changed.emit()
    
    def on_water_method_changed(self, method_text: str):
        """Handle water calculation method change"""
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
        
        self.settings_changed.emit()
    
    def on_water_value_changed(self):
        """Handle water calculation value change"""
        value = self.water_value_spinbox.value()
        self.calculator.set_water_calc_method(self.calculator.water_calc_method, value)
        self.settings_changed.emit()
    
    def on_superfat_changed(self):
        """Handle superfat change"""
        self.calculator.set_superfat(self.superfat_spinbox.value())
        self.settings_changed.emit()
    
    def on_lye_type_changed(self, lye_type: str):
        """Handle lye type change"""
        self.calculator.set_lye_type(lye_type)
        self.settings_changed.emit()


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
