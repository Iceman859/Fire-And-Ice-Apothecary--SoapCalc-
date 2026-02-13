"""
Widgets for the Gummy Calculator module.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, 
    QDoubleSpinBox, QPushButton, QGroupBox, QGridLayout, QSpinBox,
    QFormLayout, QFormLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from src.models.gummy_calculator import GummyCalculator
from src.data.gummy_ingredients import get_all_gummy_ingredients

class GummyIngredientWidget(QWidget):
    """Widget to add ingredients to the gummy recipe."""
    
    ingredient_added = pyqtSignal()

    def __init__(self, calculator: GummyCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Ingredient Selection
        layout.addWidget(QLabel("Ingredient:"))
        self.ing_combo = QComboBox()
        self.ing_combo.setEditable(True)
        self.ing_combo.addItems(get_all_gummy_ingredients())
        layout.addWidget(self.ing_combo, 2)

        # Weight Input
        layout.addWidget(QLabel("Weight:"))
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 10000)
        self.weight_spin.setValue(0.0)
        layout.addWidget(self.weight_spin, 1)

        # Unit Selection
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["g", "oz", "lbs"])
        self.unit_combo.setFixedWidth(60)
        layout.addWidget(self.unit_combo)

        # Add Button
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_ingredient)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def add_ingredient(self):
        name = self.ing_combo.currentText()
        val = self.weight_spin.value()
        unit = self.unit_combo.currentText()
        
        # Basic unit conversion
        weight_grams = val
        if unit == "oz":
            weight_grams = val * 28.3495
        elif unit == "lbs":
            weight_grams = val * 453.592
            
        if weight_grams > 0:
            self.calculator.add_ingredient(name, weight_grams)
            self.weight_spin.setValue(0)
            self.ingredient_added.emit()


class GummyResultsWidget(QWidget):
    """Widget to display Brix and water loss calculations."""
    
    def __init__(self, calculator: GummyCalculator, cost_manager=None):
        super().__init__()
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        group = QGroupBox("Batch Calculations")
        grid = QGridLayout()
        
        # Labels
        grid.addWidget(QLabel("Total Initial Weight:"), 0, 0)
        self.lbl_total_weight = QLabel("0.00 g")
        self.lbl_total_weight.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.lbl_total_weight, 0, 1)
        
        grid.addWidget(QLabel("Total Soluble Solids:"), 1, 0)
        self.lbl_solids = QLabel("0.00 g")
        self.lbl_solids.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.lbl_solids, 1, 1)
        
        grid.addWidget(QLabel("Target Final Weight:"), 2, 0)
        self.lbl_final_weight = QLabel("0.00 g")
        self.lbl_final_weight.setToolTip("The estimated final weight of your batch after cooking to the target Brix.")
        self.lbl_final_weight.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.lbl_final_weight, 2, 1)
        
        grid.addWidget(QLabel("Water to Boil Off:"), 3, 0)
        self.lbl_boil_off = QLabel("0.00 g")
        self.lbl_boil_off.setStyleSheet("font-weight: bold; color: #4fc3f7;") # Light blue accent
        self.lbl_boil_off.setToolTip("This is the key value. Cook your batch until it has lost this much weight to ensure shelf-stability.")
        self.lbl_boil_off.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.lbl_boil_off, 3, 1)
        
        grid.addWidget(QLabel("Doctoring Ratio:"), 4, 0)
        self.lbl_ratio = QLabel("N/A")
        self.lbl_ratio.setToolTip("Target Sugar:Syrup ratio is typically 1.5:1")
        self.lbl_ratio.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.lbl_ratio, 4, 1)
        
        grid.addWidget(QLabel("Total Batch Cost:"), 5, 0)
        self.lbl_cost = QLabel("$0.00")
        self.lbl_cost.setAlignment(Qt.AlignmentFlag.AlignRight)
        grid.addWidget(self.lbl_cost, 5, 1)
        
        group.setLayout(grid)
        layout.addWidget(group)
        self.setLayout(layout)
        
    def update_results(self):
        self.lbl_total_weight.setText(f"{self.calculator.total_weight:.2f} g")
        self.lbl_solids.setText(f"{self.calculator.calculate_total_solids():.2f} g")
        self.lbl_final_weight.setText(f"{self.calculator.calculate_estimated_yield():.2f} g")
        self.lbl_boil_off.setText(f"{self.calculator.calculate_water_to_remove():.2f} g")
        self.lbl_ratio.setText(self.calculator.get_doctoring_ratio())
        
        # Calculate total cost
        total_cost = 0.0
        if self.cost_manager:
            for name, weight in self.calculator.ingredients.items():
                total_cost += weight * self.cost_manager.get_cost_per_gram(name)
        self.lbl_cost.setText(f"${total_cost:.2f}")


class GummyMoldWidget(QWidget):
    """Widget to estimate batch size based on mold capacity."""
    
    recipe_scaled = pyqtSignal()

    def __init__(self, calculator: GummyCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        group = QGroupBox("Mold Volume Estimator")
        layout = QGridLayout()
        
        layout.addWidget(QLabel("Cavity Count:"), 0, 0)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 10000)
        self.count_spin.setValue(50)
        self.count_spin.valueChanged.connect(self.calculate)
        layout.addWidget(self.count_spin, 0, 1)
        
        layout.addWidget(QLabel("Vol/Cavity (ml):"), 1, 0)
        self.vol_spin = QDoubleSpinBox()
        self.vol_spin.setRange(0.1, 500.0)
        self.vol_spin.setValue(3.5)
        self.vol_spin.setSingleStep(0.1)
        self.vol_spin.valueChanged.connect(self.calculate)
        layout.addWidget(self.vol_spin, 1, 1)
        
        layout.addWidget(QLabel("Total Volume:"), 2, 0)
        self.lbl_total_vol = QLabel("0.0 ml")
        layout.addWidget(self.lbl_total_vol, 2, 1)
        
        layout.addWidget(QLabel("Est. Weight (g):"), 3, 0)
        self.lbl_est_weight = QLabel("0.0 g")
        self.lbl_est_weight.setToolTip("Assumes density of 1.35 g/ml")
        layout.addWidget(self.lbl_est_weight, 3, 1)
        
        scale_btn = QPushButton("Scale Recipe to this Weight")
        scale_btn.clicked.connect(self.scale_recipe)
        layout.addWidget(scale_btn, 4, 0, 1, 2)
        
        group.setLayout(layout)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(group)
        self.layout().setContentsMargins(0,0,0,0)
        self.calculate()

    def calculate(self):
        count = self.count_spin.value()
        vol = self.vol_spin.value()
        
        total_vol = count * vol
        weight = self.calculator.calculate_mold_requirements(count, vol)
        
        self.lbl_total_vol.setText(f"{total_vol:.1f} ml")
        self.lbl_est_weight.setText(f"{weight:.1f} g")

    def scale_recipe(self):
        count = self.count_spin.value()
        vol = self.vol_spin.value()
        target_weight = self.calculator.calculate_mold_requirements(count, vol)
        
        if target_weight > 0:
            self.calculator.scale_recipe(target_weight)
            self.recipe_scaled.emit()


class GummySettingsWidget(QWidget):
    """Widget for gummy calculator settings (Theme, etc.)"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, calculator: GummyCalculator):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        # Target Brix
        self.brix_spin = QDoubleSpinBox()
        self.brix_spin.setRange(50.0, 90.0)
        self.brix_spin.setSingleStep(0.5)
        self.brix_spin.setValue(self.calculator.target_brix)
        self.brix_spin.setToolTip("The target sugar concentration (Brix) for the final product. 78-80 is standard for shelf-stable gummies.")
        self.brix_spin.valueChanged.connect(self.on_brix_changed)
        layout.addRow(QLabel("Target Brix:"), self.brix_spin)
        
        # Theme Accent
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Blue", "Green", "Red", "Purple", "Orange", "Teal"])
        self.theme_combo.currentTextChanged.connect(lambda: self.settings_changed.emit())
        layout.addRow(QLabel("Theme Accent:"), self.theme_combo)
        
        self.setLayout(layout)

    def on_brix_changed(self, value: float):
        self.calculator.target_brix = value
        self.settings_changed.emit()


class GummyBloomWidget(QWidget):
    """
    Tool to convert gelatin weights between different Bloom strengths.
    Formula: Mass1 * sqrt(Bloom1) = Mass2 * sqrt(Bloom2)
    """
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        group = QGroupBox("Gelatin Bloom Converter")
        layout = QGridLayout()
        
        # Source
        layout.addWidget(QLabel("<b>Original Recipe:</b>"), 0, 0, 1, 2)
        layout.addWidget(QLabel("Weight (g):"), 1, 0)
        self.src_weight = QDoubleSpinBox()
        self.src_weight.setRange(0, 10000)
        self.src_weight.setValue(20.0)
        layout.addWidget(self.src_weight, 1, 1)
        
        layout.addWidget(QLabel("Bloom Strength:"), 2, 0)
        self.src_bloom = QSpinBox()
        self.src_bloom.setRange(50, 350)
        self.src_bloom.setValue(250)
        self.src_bloom.setSingleStep(10)
        layout.addWidget(self.src_bloom, 2, 1)
        
        # Target
        layout.addWidget(QLabel("<b>My Inventory:</b>"), 3, 0, 1, 2)
        layout.addWidget(QLabel("New Bloom Strength:"), 4, 0)
        self.target_bloom = QSpinBox()
        self.target_bloom.setRange(50, 350)
        self.target_bloom.setValue(160)
        self.target_bloom.setSingleStep(10)
        layout.addWidget(self.target_bloom, 4, 1)
        
        # Result
        calc_btn = QPushButton("Calculate Conversion")
        calc_btn.clicked.connect(self.calculate)
        layout.addWidget(calc_btn, 5, 0, 1, 2)
        
        self.result_lbl = QLabel("Required Weight: 0.00 g")
        self.result_lbl.setStyleSheet("font-weight: bold; font-size: 14px; color: #4fc3f7;")
        self.result_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_lbl, 6, 0, 1, 2)
        
        group.setLayout(layout)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(group)
        main_layout.addStretch()
        self.setLayout(main_layout)
        
        self.calculate()
        
    def calculate(self):
        import math
        w1 = self.src_weight.value()
        b1 = self.src_bloom.value()
        b2 = self.target_bloom.value()
        
        if b2 <= 0: return
        
        # Mass2 = Mass1 * sqrt(Bloom1) / sqrt(Bloom2)
        # Mass2 = Mass1 * sqrt(Bloom1 / Bloom2)
        w2 = w1 * math.sqrt(b1 / b2)
        
        self.result_lbl.setText(f"Required Weight: {w2:.2f} g")