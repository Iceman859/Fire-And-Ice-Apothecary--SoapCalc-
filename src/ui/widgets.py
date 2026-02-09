"""UI Widgets"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QCompleter, QGroupBox,
    QGridLayout
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


class OilInputWidget(QWidget):
    """Widget for adding oils to recipe"""
    
    oil_added = pyqtSignal()
    
    def __init__(self, calculator: SoapCalculator):
        super().__init__()
        self.calculator = calculator
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
        completer = QCompleter(names)
        self.oil_combo.setCompleter(completer)
        layout.addWidget(self.oil_combo, 2)
        
        # Weight input with unit selector
        layout.addWidget(QLabel("Weight:"))
        self.weight_spinbox = QDoubleSpinBox()
        self.weight_spinbox.setRange(0, 10000)
        self.weight_spinbox.setValue(100)
        layout.addWidget(self.weight_spinbox, 1)
        
        self.weight_unit_combo = QComboBox()
        self.weight_unit_combo.addItems(["g", "oz", "lbs"])
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
            # Convert to grams for storage
            unit_map = {"g": "grams", "oz": "ounces", "lbs": "pounds"}
            weight_grams = self.calculator.convert_to_grams(weight, unit_map[unit])
            self.calculator.add_oil(oil_name, weight_grams)
            self.weight_spinbox.setValue(100)
            self.oil_added.emit()
            
    def set_unit_system(self, unit_system: str):
        """Update default unit selection based on global settings"""
        unit_map = {"grams": "g", "ounces": "oz", "pounds": "lbs"}
        self.weight_unit_combo.setCurrentText(unit_map.get(unit_system, "g"))


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
        self.add_combo.addItems(get_all_additive_names())
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
        self.add_spin.setValue(3.0)
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
        self.add_weight_spin.setValue(50.0)
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
            self.add_spin.setValue(3.0)
            self.add_weight_spin.setValue(50.0)
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


class CalculationResultsWidget(QWidget):
    """Widget for displaying calculation results"""
    
    def __init__(self, calculator: SoapCalculator = None):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()
    
    def setup_ui(self):
        """Setup results display"""
        layout = QVBoxLayout()
        
        # Batch Weights
        self.weights_group = QGroupBox("Batch Weights")
        w_layout = QGridLayout()
        
        self.weight_labels = {}
        weight_keys = ["Total Oil Weight", "Water Weight", "Lye Weight", "Total Batch Weight"]
        
        for i, key in enumerate(weight_keys):
            w_layout.addWidget(QLabel(f"{key}:"), i, 0)
            val_lbl = QLabel("0.00")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            w_layout.addWidget(val_lbl, i, 1)
            self.weight_labels[key] = val_lbl
            
        self.weights_group.setLayout(w_layout)
        layout.addWidget(self.weights_group)
        
        # Predicted Qualities
        self.qualities_group = QGroupBox("Predicted Qualities")
        q_layout = QGridLayout()
        
        self.quality_labels_display = {}
        quality_keys = ["Hardness", "Conditioning", "Bubbly", "Creamy", "Iodine", "INS"]
        
        for i, key in enumerate(quality_keys):
            q_layout.addWidget(QLabel(f"{key}:"), i, 0)
            val_lbl = QLabel("0.0")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            q_layout.addWidget(val_lbl, i, 1)
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
        
        # Batch Weights
        weights_map = {
            "Total Oil Weight": properties['total_oil_weight'],
            "Water Weight": properties['water_weight'],
            "Lye Weight": properties['lye_weight'],
            "Total Batch Weight": properties['total_batch_weight']
        }
        
        for key, grams in weights_map.items():
            if key in self.weight_labels:
                self.weight_labels[key].setText(f"{convert_weight(grams)} {unit_abbr}")
            
        # Soap Qualities
        qualities = properties.get('relative_qualities', {})
        
        quality_map = {
            "Hardness": qualities.get('Hardness', 0),
            "Conditioning": qualities.get('Moisturizing', 0),
            "Bubbly": qualities.get('Fluffy Lather', 0),
            "Creamy": qualities.get('Stable Lather', 0),
            "Iodine": properties.get('iodine_value', 0),
            "INS": properties.get('ins_value', 0)
        }
        
        for key, val in quality_map.items():
            if key in self.quality_labels_display:
                self.quality_labels_display[key].setText(f"{float(val):.1f}")


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
