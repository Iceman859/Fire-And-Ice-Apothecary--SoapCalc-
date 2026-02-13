"""
Gummy Calculator Window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QTabWidget, QPushButton,
    QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt, QSettings
from src.models.gummy_calculator import GummyCalculator
from src.models.gummy_recipe import GummyRecipe, GummyRecipeManager
from src.models.cost_manager import CostManager
from src.ui.gummy_widgets import (
    GummyIngredientWidget, GummyResultsWidget, GummyMoldWidget, 
    GummySettingsWidget, GummyBloomWidget
)
from src.ui.widgets import RecipeNotesWidget

class GummyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fire & Ice Apothecary (Gummy Calculator)")
        self.setGeometry(100, 100, 1200, 800)
        
        self.calculator = GummyCalculator()
        self.recipe_manager = GummyRecipeManager()
        self.cost_manager = CostManager()
        self.current_recipe = GummyRecipe()
        self._settings = QSettings("FireAndIceApothecary", "SoapCalc")
        
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        label = QLabel("Gummy Calculator Module")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(label)
        
        # Tabs
        tabs = QTabWidget()
        
        # --- Calculator Tab ---
        calc_tab = QWidget()
        calc_layout = QVBoxLayout()
        calc_layout.setContentsMargins(5, 5, 5, 5)
        
        # Input Widget
        self.input_widget = GummyIngredientWidget(self.calculator)
        self.input_widget.ingredient_added.connect(self.update_ui)
        layout.addWidget(self.input_widget)
        
        # Main Content Area (Table + Results)
        content_layout = QHBoxLayout()
        
        # Ingredients Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Ingredient", "Weight (g)", "Cost"])
        content_layout.addWidget(self.table, 2)
        
        # Right Column (Results + Mold Estimator)
        right_col = QVBoxLayout()
        self.results_widget = GummyResultsWidget(self.calculator, self.cost_manager)
        right_col.addWidget(self.results_widget)
        
        self.mold_widget = GummyMoldWidget(self.calculator)
        self.mold_widget.recipe_scaled.connect(self.update_ui)
        right_col.addWidget(self.mold_widget)
        
        # Recipe Operations
        right_col.addWidget(QLabel("Recipe Operations:"))
        btn_layout = QHBoxLayout()
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_recipe)
        btn_layout.addWidget(new_btn)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_recipe)
        btn_layout.addWidget(save_btn)
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_recipe)
        btn_layout.addWidget(load_btn)
        right_col.addLayout(btn_layout)
        
        right_col.addStretch()
        
        content_layout.addLayout(right_col, 1)
        
        calc_layout.addLayout(content_layout)
        calc_tab.setLayout(calc_layout)
        tabs.addTab(calc_tab, "Calculator")
        
        # --- Notes Tab ---
        notes_tab = QWidget()
        notes_layout = QVBoxLayout()
        self.notes_widget = RecipeNotesWidget()
        notes_layout.addWidget(self.notes_widget)
        notes_tab.setLayout(notes_layout)
        tabs.addTab(notes_tab, "Notes")
        
        # --- Tools Tab (Bloom Converter) ---
        tools_tab = QWidget()
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(GummyBloomWidget())
        tools_tab.setLayout(tools_layout)
        tabs.addTab(tools_tab, "Tools")
        
        # --- Settings Tab ---
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        self.settings_widget = GummySettingsWidget(self.calculator)
        self.settings_widget.settings_changed.connect(self.update_theme_from_settings)
        self.settings_widget.settings_changed.connect(self.save_preferences)
        self.settings_widget.settings_changed.connect(self.update_ui)
        settings_layout.addWidget(self.settings_widget)
        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, "Settings")
        
        layout.addWidget(tabs)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        # Apply Theme and Load Settings
        self.load_preferences()
        self.showMaximized()

    def update_ui(self):
        """Refresh table and results."""
        # Update Table
        self.table.setRowCount(len(self.calculator.ingredients))
        for row, (name, weight) in enumerate(self.calculator.ingredients.items()):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(f"{weight:.2f}"))
            
            # Calculate cost
            cost = weight * self.cost_manager.get_cost_per_gram(name)
            self.table.setItem(row, 2, QTableWidgetItem(f"${cost:.2f}"))
            
        # Update Results
        self.results_widget.update_results()

    def load_preferences(self):
        """Load settings from QSettings"""
        theme = self._settings.value('theme_accent', 'Blue')
        brix = float(self._settings.value('gummy_target_brix', 78.0))

        self.calculator.target_brix = brix
        self.settings_widget.brix_spin.setValue(brix)
        self.settings_widget.theme_combo.setCurrentText(theme)

        self.update_theme_from_settings()

    def save_preferences(self):
        """Save settings to QSettings"""
        self._settings.setValue('theme_accent', self.settings_widget.theme_combo.currentText())
        self._settings.setValue('gummy_target_brix', self.calculator.target_brix)

    def update_theme_from_settings(self):
        """Update application theme based on settings selection"""
        theme_name = self.settings_widget.theme_combo.currentText()
        colors = self.get_theme_colors(theme_name)
        self.apply_dark_theme(colors["accent"], colors["hover"], colors["pressed"])

    def get_theme_colors(self, name):
        """Get colors for theme name"""
        themes = {
            "Blue": {"accent": "#0d47a1", "hover": "#1565c0", "pressed": "#0a3d91"},
            "Green": {"accent": "#2e7d32", "hover": "#388e3c", "pressed": "#1b5e20"},
            "Red": {"accent": "#c62828", "hover": "#d32f2f", "pressed": "#b71c1c"},
            "Purple": {"accent": "#6a1b9a", "hover": "#7b1fa2", "pressed": "#4a148c"},
            "Orange": {"accent": "#ef6c00", "hover": "#f57c00", "pressed": "#e65100"},
            "Teal": {"accent": "#00695c", "hover": "#00796b", "pressed": "#004d40"},
        }
        return themes.get(name, themes["Blue"])

    def new_recipe(self):
        """Create a new gummy recipe."""
        self.calculator.ingredients.clear()
        self.calculator._calculate_totals()
        self.current_recipe = GummyRecipe()
        self.notes_widget.set_notes("")
        self.update_ui()
        self.statusBar().showMessage("New recipe created")

    def save_recipe(self):
        """Save the current recipe."""
        name, ok = QInputDialog.getText(self, "Save Recipe", "Recipe Name:", text=self.current_recipe.name)
        if ok and name:
            self.current_recipe.name = name
            # Update recipe object from calculator and UI
            calc_data = self.calculator.get_recipe_dict()
            self.current_recipe.ingredients = calc_data["ingredients"]
            self.current_recipe.target_brix = calc_data["target_brix"]
            self.current_recipe.notes = self.notes_widget.get_notes()
            
            try:
                filepath = self.recipe_manager.save_recipe(self.current_recipe)
                self.statusBar().showMessage(f"Recipe saved to {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save recipe: {str(e)}")

    def load_recipe(self):
        """Load a recipe from file."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Recipe", "gummy_recipes", "JSON Files (*.json)")
        if filepath:
            try:
                recipe = self.recipe_manager.load_recipe(filepath)
                if recipe:
                    self.current_recipe = recipe
                    self.calculator.load_recipe_dict(recipe.to_dict())
                    self.notes_widget.set_notes(recipe.notes)
                    self.update_ui()
                    self.statusBar().showMessage(f"Loaded recipe: {recipe.name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load recipe: {str(e)}")
    def apply_dark_theme(self, accent_color="#0d47a1", hover_color="#1565c0", pressed_color="#0a3d91"):
        """Apply dark theme stylesheet"""
        dark_stylesheet = f"""
        QMainWindow, QWidget, QMainWindow::title {{
            background-color: #1e1e1e;
            color: #e0e0e0;
        }}
        
        QLabel {{
            color: #e0e0e0;
        }}
        
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            padding: 5px;
            border-radius: 3px;
        }}
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, 
        QComboBox:focus, QTextEdit:focus {{
            border: 1px solid {accent_color};
            background-color: #323232;
        }}
        
        QPushButton {{
            background-color: {accent_color};
            color: #e0e0e0;
            border: none;
            padding: 8px 16px;
            border-radius: 3px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
        
        QTableWidget, QTableWidget::item {{
            background-color: #2d2d2d;
            color: #e0e0e0;
            gridline-color: #3d3d3d;
        }}
        
        QTableWidget::item:selected {{
            background-color: {accent_color};
        }}
        
        QHeaderView::section {{
            background-color: #424242;
            color: #e0e0e0;
            padding: 5px;
            border: 1px solid #3d3d3d;
        }}
        
        QTabWidget::pane {{
            border: 1px solid #3d3d3d;
        }}
        
        QTabBar::tab {{
            background-color: #2d2d2d;
            color: #a0a0a0;
            padding: 8px 20px;
            border: 1px solid #3d3d3d;
        }}
        
        QTabBar::tab:selected {{
            background-color: {accent_color};
            color: #e0e0e0;
        }}
        
        QScrollBar:vertical {{
            background-color: #2d2d2d;
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: #545454;
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: #656565;
        }}
        
        QStatusBar {{
            background-color: #2d2d2d;
            color: #e0e0e0;
            border-top: 1px solid #3d3d3d;
        }}
        """
        self.setStyleSheet(dark_stylesheet)