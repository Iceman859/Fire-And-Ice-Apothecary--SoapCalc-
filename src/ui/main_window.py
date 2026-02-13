"""Main application window"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QSplitter,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QIcon, QFont
import json

from src.models import SoapCalculator, Recipe, RecipeManager
from src.models.cost_manager import CostManager
from src.data import get_all_oil_names
from .widgets import (
    OilInputWidget, CalculationResultsWidget, SettingsWidget,
    AdditiveInputWidget, RecipeParametersWidget,
    RecipeNotesWidget, RecipeReportWidget, InventoryCostWidget, FragranceWidget
)
from .widgets import FABreakdownWidget


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fire & Ice Apothecary (Soap Calculator)")
        self.setGeometry(100, 100, 1400, 900)
        self.showMaximized()
        
        # Initialize calculator and recipe manager
        self.calculator = SoapCalculator()
        self.recipe_manager = RecipeManager("recipes")
        self.cost_manager = CostManager()
        self.current_recipe = Recipe()
        # QSettings for persisting preferences across launches
        self._settings = QSettings("FireAndIceApothecary", "SoapCalc")
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create UI
        self.setup_ui()
        # Load persisted preferences (units, water method, superfat, lye type)
        self.load_preferences()
        
        # Connect signals
        self.connect_signals()
        # Internal flags for table signal suppression
        self._suppress_oils_table_signals = False
        self._suppress_additives_table_signals = False
    
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

    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Fire & Ice Apothecary - Soap Calculator")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Recipe Tab
        recipe_tab = self.create_recipe_tab()
        tabs.addTab(recipe_tab, "Recipe Calculator")
        
        # FA Breakdown Tab
        fa_tab = self.create_fa_tab()
        tabs.addTab(fa_tab, "FA Breakdown")
        
        # Notes Tab
        self.notes_tab = self.create_notes_tab()
        tabs.addTab(self.notes_tab, "Notes")
        
        # View/Print Tab
        self.print_tab = self.create_print_tab()
        tabs.addTab(self.print_tab, "View / Print")
        
        # Inventory/Cost Tab
        self.inventory_tab = self.create_inventory_tab()
        tabs.addTab(self.inventory_tab, "Inventory/Cost")
        
        # Settings Tab
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "Settings")
        
        main_layout.addWidget(tabs)
        
        # Connect tab change to refresh print view
        tabs.currentChanged.connect(self.on_tab_changed)
        self.tabs = tabs
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        central_widget.setLayout(main_layout)
    
    def create_recipe_tab(self):
        """Create the recipe calculator tab"""
        tab = QWidget()
        layout = QHBoxLayout()
        
        # --- Column 1: Parameters & Fragrance (Left) ---
        col1_content = QWidget()
        col1_layout = QVBoxLayout(col1_content)
        col1_layout.setContentsMargins(5, 5, 5, 5)
        
        col1_layout.addWidget(QLabel("Recipe Parameters:"))
        self.recipe_settings = RecipeParametersWidget(self.calculator)
        col1_layout.addWidget(self.recipe_settings)
        
        col1_layout.addWidget(QLabel("Fragrance:"))
        self.fragrance_widget = FragranceWidget(self.calculator)
        col1_layout.addWidget(self.fragrance_widget)
        
        col1_layout.addStretch()
        
        col1_scroll = QScrollArea()
        col1_scroll.setWidgetResizable(True)
        col1_scroll.setWidget(col1_content)
        col1_scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        # --- Column 2: Oils & Additives (Middle) ---
        col2_widget = QWidget()
        col2_layout = QVBoxLayout(col2_widget)
        col2_layout.setContentsMargins(5, 5, 5, 5)
        
        # Oil Input Area
        self.oil_input_widget = OilInputWidget(self.calculator)
        col2_layout.addWidget(self.oil_input_widget)
        
        # Table for oils in recipe
        self.oils_table = QTableWidget()
        self.oils_table.setColumnCount(4)
        self.update_oils_table_headers()
        self.oils_table.setColumnWidth(0, 180)
        self.oils_table.setColumnWidth(1, 80)
        self.oils_table.setColumnWidth(2, 70)
        self.oils_table.setColumnWidth(3, 70)
        col2_layout.addWidget(self.oils_table)

        # enable inline edits and removal for oils
        self.oils_table.cellChanged.connect(self.on_oil_cell_changed)
        remove_oil_btn = QPushButton("Remove Selected Oil")
        remove_oil_btn.clicked.connect(self.remove_selected_oil)
        col2_layout.addWidget(remove_oil_btn)
        
        # Manage Ingredients Button
        manage_ing_btn = QPushButton("Manage Custom Ingredients")
        manage_ing_btn.clicked.connect(self.open_ingredient_editor)
        col2_layout.addWidget(manage_ing_btn)

        # Additives Input Area
        self.additive_widget = AdditiveInputWidget(self.calculator)
        col2_layout.addWidget(self.additive_widget)
        
        # Additives table (editable) - shown below oil input
        self.additives_table = QTableWidget()
        self.additives_table.setColumnCount(3)
        unit_abbr = self.calculator.get_unit_abbreviation()
        self.additives_table.setHorizontalHeaderLabels(["Additive", f"Amount ({unit_abbr})", "Water Replacement"])
        self.additives_table.setColumnWidth(0, 180)
        self.additives_table.setColumnWidth(1, 90)
        self.additives_table.setColumnWidth(2, 100)
        col2_layout.addWidget(self.additives_table)
        self.additives_table.cellChanged.connect(self.on_additive_cell_changed)
        remove_add_btn = QPushButton("Remove Selected Additive")
        remove_add_btn.clicked.connect(self.remove_selected_additive)
        col2_layout.addWidget(remove_add_btn)

        # --- Column 3: Results & Operations (Right) ---
        col3_content = QWidget()
        col3_layout = QVBoxLayout(col3_content)
        col3_layout.setContentsMargins(5, 5, 5, 5)
        
        col3_layout.addWidget(QLabel("Calculation Results:"))
        self.results_widget = CalculationResultsWidget(self.calculator, self.cost_manager)
        col3_layout.addWidget(self.results_widget)
        
        # Scaling controls
        col3_layout.addWidget(QLabel("Scale Recipe:"))
        scale_layout = QHBoxLayout()
        self.scale_label = QLabel("Total Oil Weight (g):")
        scale_layout.addWidget(self.scale_label)
        self.scale_spinbox = QDoubleSpinBox()
        self.scale_spinbox.setRange(0, 10000)
        self.scale_spinbox.setValue(32)
        scale_layout.addWidget(self.scale_spinbox)
        scale_btn = QPushButton("Scale Recipe")
        scale_btn.clicked.connect(self.scale_recipe)
        scale_layout.addWidget(scale_btn)
        col3_layout.addLayout(scale_layout)
        
        # Connect percentage callback to use the scale spinbox as target weight
        self.oil_input_widget.target_weight_callback = self.get_target_batch_weight
        
        # Recipe management buttons
        col3_layout.addWidget(QLabel("Recipe Operations:"))
        button_layout = QHBoxLayout()
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_recipe)
        button_layout.addWidget(new_btn)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_recipe)
        button_layout.addWidget(save_btn)
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_recipe)
        button_layout.addWidget(load_btn)
        col3_layout.addLayout(button_layout)
        
        col3_layout.addStretch()
        
        col3_scroll = QScrollArea()
        col3_scroll.setWidgetResizable(True)
        col3_scroll.setWidget(col3_content)
        col3_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(col1_scroll)
        splitter.addWidget(col2_widget)
        splitter.addWidget(col3_scroll)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 4)
        
        layout.addWidget(splitter)
        tab.setLayout(layout)
        return tab
    
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.settings_widget = SettingsWidget(self.calculator)
        layout.addWidget(self.settings_widget)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_fa_tab(self):
        """Create the fatty-acid breakdown tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        self.fa_widget = FABreakdownWidget(self.calculator)
        layout.addWidget(self.fa_widget)
        tab.setLayout(layout)
        return tab
    
    def create_notes_tab(self):
        """Create the recipe notes tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        self.notes_widget = RecipeNotesWidget()
        layout.addWidget(self.notes_widget)
        tab.setLayout(layout)
        return tab

    def create_print_tab(self):
        """Create the view/print tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        self.report_widget = RecipeReportWidget(self.calculator)
        layout.addWidget(self.report_widget)
        tab.setLayout(layout)
        return tab

    def create_inventory_tab(self):
        """Create the inventory/cost tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        self.inventory_widget = InventoryCostWidget(self.cost_manager)
        layout.addWidget(self.inventory_widget)
        tab.setLayout(layout)
        return tab
    
    def connect_signals(self):
        """Connect widget signals to slots"""
        # Sync settings to calculator first
        self.settings_widget.settings_changed.connect(self.sync_settings_to_calculator)
        self.settings_widget.settings_changed.connect(self.update_input_units)
        self.settings_widget.settings_changed.connect(self.update_theme_from_settings)
        # Sync recipe parameters
        self.recipe_settings.parameters_changed.connect(self.update_results)
        self.recipe_settings.parameters_changed.connect(self.save_preferences)
        
        self.oil_input_widget.oil_added.connect(self.update_oils_table)
        self.oil_input_widget.oil_added.connect(self.update_results)
        self.settings_widget.settings_changed.connect(self.update_results)
        self.settings_widget.settings_changed.connect(self.update_scale_label)
        # Persist preferences whenever settings change
        self.settings_widget.settings_changed.connect(self.save_preferences)
        self.additive_widget.additive_added.connect(self.update_additives_table)
        self.additive_widget.additive_added.connect(self.update_results)
        # ensure tables update when settings change (units etc.)
        self.settings_widget.settings_changed.connect(self.update_oils_table)
        self.settings_widget.settings_changed.connect(self.update_additives_table)

        # Fragrance connections
        self.fragrance_widget.fragrance_added.connect(self.update_additives_table)
        self.fragrance_widget.fragrance_added.connect(self.update_results)

    def on_tab_changed(self, index):
        """Handle tab changes"""
        # If switching to Print tab (index check or widget check)
        if self.tabs.widget(index) == self.print_tab:
            notes = self.notes_widget.get_notes()
            self.report_widget.refresh_report(self.current_recipe.name or "Current Recipe", notes)

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

    def update_theme_from_settings(self):
        """Update application theme based on settings selection"""
        theme_name = self.settings_widget.theme_combo.currentText()
        colors = self.get_theme_colors(theme_name)
        self.apply_dark_theme(colors["accent"], colors["hover"], colors["pressed"])

    def update_input_units(self):
        """Update input widgets with new unit system"""
        unit = self.calculator.unit_system
        self.oil_input_widget.set_unit_system(unit)
        self.additive_widget.set_unit_system(unit)

    def update_additives_table(self):
        """Update additives table (simple display)"""
        additives = self.calculator.additives
        total_oil = self.calculator.get_total_oil_weight()
        rows = len(additives)
        # suppress signals while updating
        self._suppress_additives_table_signals = True
        # update header to reflect current unit
        unit_abbr = self.calculator.get_unit_abbreviation()
        self.additives_table.setHorizontalHeaderLabels(["Additive", f"Amount ({unit_abbr})", "Water Replacement"])
        self.additives_table.setRowCount(rows)
        from src.data.additives import get_additive_info
        for row, (name, grams) in enumerate(sorted(additives.items())):
            # display amount in current unit
            display_amount = self.calculator.convert_weight(grams, self.calculator.unit_system)
            name_item = QTableWidgetItem(name)
            amt_item = QTableWidgetItem(f"{display_amount:.2f}")
            info = get_additive_info(name)
            is_repl = info.get('is_water_replacement', False)
            repl_item = QTableWidgetItem("Yes" if is_repl else "No")
            self.additives_table.setItem(row, 0, name_item)
            self.additives_table.setItem(row, 1, amt_item)
            self.additives_table.setItem(row, 2, repl_item)
        self._suppress_additives_table_signals = False
    
    def update_oils_table(self):
        """Update the oils table from calculator"""
        unit_abbr = self.calculator.get_unit_abbreviation()
        self.update_oils_table_headers()
        # suppress signals while updating table
        self._suppress_oils_table_signals = True
        self.oils_table.setRowCount(len(self.calculator.oils))
        total_oil = self.calculator.get_total_oil_weight()
        # keep mapping from rows to oil names for edits
        self._oils_rows = []

        for row, (oil_name, weight) in enumerate(sorted(self.calculator.oils.items())):
            percentage = (weight / total_oil * 100) if total_oil > 0 else 0
            # Convert weight to display unit
            display_weight = self.calculator.convert_weight(weight, self.calculator.unit_system)

            # Calculate cost
            cost_per_g = self.cost_manager.get_cost_per_gram(oil_name)
            cost = weight * cost_per_g

            name_item = QTableWidgetItem(oil_name)
            weight_item = QTableWidgetItem(f"{display_weight:.2f}")
            pct_item = QTableWidgetItem(f"{percentage:.2f}")
            cost_item = QTableWidgetItem(f"${cost:.2f}")

            self.oils_table.setItem(row, 0, name_item)
            self.oils_table.setItem(row, 1, weight_item)
            self.oils_table.setItem(row, 2, pct_item)
            self.oils_table.setItem(row, 3, cost_item)

            self._oils_rows.append(oil_name)

        self._suppress_oils_table_signals = False
    
    def update_oils_table_headers(self):
        """Update table headers with current unit"""
        unit_abbr = self.calculator.get_unit_abbreviation()
        self.oils_table.setHorizontalHeaderLabels(["Oil Name", f"Weight ({unit_abbr})", "% of Oils", "Cost"])
    
    def update_scale_label(self):
        """Update scale label with current unit"""
        unit_abbr = self.calculator.get_unit_abbreviation()
        self.scale_label.setText(f"Total Oil Weight ({unit_abbr}):")
    
    def update_results(self):
        """Update calculation results"""
        properties = self.calculator.get_batch_properties()
        self.results_widget.update_results(properties, self.calculator.unit_system, self.current_recipe.name)
        # update FA breakdown tab if present
        try:
            if hasattr(self, 'fa_widget') and self.fa_widget:
                self.fa_widget.update_fa(properties, self.calculator.unit_system)
        except Exception:
            pass
        self.update_oils_table()
        self.update_additives_table()
        
        # Update fragrance calc
        if hasattr(self, 'fragrance_widget'):
            self.fragrance_widget.update_calculation()
    
    def get_target_batch_weight(self):
        """Get target batch weight in grams for percentage calculations"""
        val = self.scale_spinbox.value()
        return self.calculator.convert_to_grams(val, self.calculator.unit_system)
    
    def scale_recipe(self):
        """Scale recipe to new weight"""
        new_weight = self.scale_spinbox.value()
        unit_abbr = self.calculator.get_unit_abbreviation()
        if new_weight > 0:
            # Convert from display unit to grams
            weight_grams = self.calculator.convert_to_grams(new_weight, self.calculator.unit_system)
            self.calculator.scale_recipe(weight_grams)
            self.update_results()
            self.statusBar().showMessage(f"Recipe scaled to {new_weight}{unit_abbr}")
    
    def new_recipe(self):
        """Create new recipe"""
        # Reset existing calculator state instead of replacing instance
        self.calculator.oils.clear()
        self.calculator.additives.clear()
        self.notes_widget.set_notes("")
        self.current_recipe = Recipe()
        # Reload defaults (this also updates results)
        self.load_preferences()
        self.statusBar().showMessage("New recipe created")
    
    def save_recipe(self):
        """Save current recipe"""
        name, ok = self._show_recipe_name_dialog("Save Recipe", self.current_recipe.name)
        if ok and name:
            self.current_recipe.name = name
            self.current_recipe.oils = self.calculator.oils.copy()
            self.current_recipe.additives = self.calculator.additives.copy()
            self.current_recipe.superfat_percent = self.calculator.superfat_percent
            self.current_recipe.water_to_lye_ratio = self.calculator.water_to_lye_ratio
            self.current_recipe.lye_type = self.calculator.lye_type
            self.current_recipe.water_calc_method = self.calculator.water_calc_method
            self.current_recipe.water_percent = self.calculator.water_percent
            self.current_recipe.lye_concentration = self.calculator.lye_concentration
            
            filepath = self.recipe_manager.save_recipe(self.current_recipe)
            
            # Manually append additives to the JSON file to ensure persistence
            if filepath:
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    data['additives'] = self.calculator.additives
                    data['notes'] = self.notes_widget.get_notes()
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=4)
                except Exception as e:
                    print(f"Error saving additives to JSON: {e}")
            
            self.statusBar().showMessage(f"Recipe saved to {filepath}")
            self.update_results()
    
    def load_recipe(self):
        """Load recipe from file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Recipe", "recipes", "Recipe files (*.json)"
        )
        if filepath:
            self.load_recipe_file(filepath)
    
    def load_recipe_file(self, filepath: str):
        """Load recipe from specified filepath"""
        recipe = self.recipe_manager.load_recipe(filepath)
        if recipe:
            self.current_recipe = recipe
            self.calculator.load_recipe_dict(recipe.to_dict())
            
            # Manually load additives from JSON to ensure they persist
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if 'additives' in data:
                        self.calculator.additives = data['additives']
                    if 'notes' in data:
                        self.notes_widget.set_notes(data['notes'])
                    else:
                        self.notes_widget.set_notes("")
            except Exception as e:
                print(f"Error loading additives from JSON: {e}")
            
            # Update UI to match loaded recipe parameters
            self.recipe_settings.blockSignals(True)
            try:
                self.recipe_settings.lye_combo.setCurrentText(self.calculator.lye_type)
                self.recipe_settings.superfat_spinbox.setValue(self.calculator.superfat_percent)
                
                method = self.calculator.water_calc_method
                method_map_rev = {
                    'ratio': 'Water:Lye Ratio',
                    'percent': 'Water % of Oils',
                    'concentration': 'Lye Concentration'
                }
                self.recipe_settings.water_method_combo.setCurrentText(method_map_rev.get(method, 'Water:Lye Ratio'))
                
                # Update water spinbox based on method
                if method == 'percent':
                    self.recipe_settings.water_value_label.setText("% of Oils:")
                    self.recipe_settings.water_value_spinbox.setRange(0, 100)
                    self.recipe_settings.water_value_spinbox.setValue(self.calculator.water_percent)
                elif method == 'concentration':
                    self.recipe_settings.water_value_label.setText("Lye % (concentration):")
                    self.recipe_settings.water_value_spinbox.setRange(1, 99)
                    self.recipe_settings.water_value_spinbox.setValue(self.calculator.lye_concentration)
                else:
                    self.recipe_settings.water_value_label.setText("Ratio:")
                    self.recipe_settings.water_value_spinbox.setRange(0.5, 5)
                    self.recipe_settings.water_value_spinbox.setValue(self.calculator.water_to_lye_ratio)
            finally:
                self.recipe_settings.blockSignals(False)

            # Enforce the currently selected unit system from settings
            current_unit_text = self.settings_widget.unit_combo.currentText()
            unit_map = {"Grams": "grams", "Ounces": "ounces", "Pounds": "pounds"}
            self.calculator.set_unit_system(unit_map.get(current_unit_text, "grams"))
            
            self.update_results()
            self.statusBar().showMessage(f"Recipe loaded: {recipe.name}")
        else:
            QMessageBox.warning(self, "Error", "Failed to load recipe")

    def load_preferences(self):
        """Load persisted preferences into the calculator and UI."""
        # Block signals to prevent overwriting settings while loading
        self.settings_widget.blockSignals(True)
        self.recipe_settings.blockSignals(True)
        try:
            # Unit System
            # Default to 'grams' if not found or invalid
            unit = self._settings.value('unit_system', 'grams')
            
            # Robustly set combo box
            combo = self.settings_widget.unit_combo
            found_unit = False
            for i in range(combo.count()):
                if combo.itemText(i).lower() == str(unit).lower():
                    combo.setCurrentIndex(i)
                    found_unit = True
                    break
            
            if not found_unit and combo.count() > 0:
                combo.setCurrentIndex(0)

            # Superfat
            superfat = float(self._settings.value('superfat_percent', 5.0))
            self.recipe_settings.superfat_spinbox.setValue(superfat)

            # Water Method
            water_method = self._settings.value('water_calc_method', 'ratio')
            # Map internal keys to UI text
            method_map_rev = {
                'ratio': 'Water:Lye Ratio',
                'percent': 'Water % of Oils',
                'concentration': 'Lye Concentration'
            }
            target_text = method_map_rev.get(water_method, 'Water:Lye Ratio')
            combo = self.recipe_settings.water_method_combo
            for i in range(combo.count()):
                if combo.itemText(i) == target_text:
                    combo.setCurrentIndex(i)
                    break

            # Water Value
            # Load all potential values with safe defaults
            w_ratio = float(self._settings.value('water_to_lye_ratio', 2.0))
            w_percent = float(self._settings.value('water_percent', 38.0))
            lye_conc = float(self._settings.value('lye_concentration', 30.0))
            
            if water_method == 'percent':
                self.recipe_settings.water_value_spinbox.setValue(w_percent)
            elif water_method == 'concentration':
                self.recipe_settings.water_value_spinbox.setValue(lye_conc)
            else:
                self.recipe_settings.water_value_spinbox.setValue(w_ratio)

            # Lye Type
            lye_type = self._settings.value('lye_type', 'NaOH')
            self.recipe_settings.lye_combo.setCurrentText(lye_type)
            
            # Theme
            theme = self._settings.value('theme_accent', 'Blue')
            self.settings_widget.theme_combo.setCurrentText(theme)
            
        except Exception as e:
            print(f"Error loading preferences: {e}")
        finally:
            self.settings_widget.blockSignals(False)
            self.recipe_settings.blockSignals(False)

        # Sync UI state to calculator to ensure consistency
        self.sync_settings_to_calculator()
        self.update_input_units()
        self.update_theme_from_settings()

        # Refresh UI to reflect loaded preferences
        self.update_scale_label()
        self.update_oils_table()
        self.update_additives_table()
        self.update_results()

    def save_preferences(self):
        """Persist current preferences to QSettings."""
        self._settings.setValue('unit_system', self.calculator.unit_system)
        self._settings.setValue('superfat_percent', float(self.calculator.superfat_percent))
        self._settings.setValue('water_calc_method', self.calculator.water_calc_method)
        self._settings.setValue('water_to_lye_ratio', float(self.calculator.water_to_lye_ratio))
        self._settings.setValue('water_percent', float(self.calculator.water_percent))
        self._settings.setValue('lye_concentration', float(self.calculator.lye_concentration))
        self._settings.setValue('lye_type', self.calculator.lye_type)
        self._settings.setValue('theme_accent', self.settings_widget.theme_combo.currentText())

    def sync_settings_to_calculator(self):
        """Ensure calculator is updated from settings widget"""
        # Update Unit
        unit_text = self.settings_widget.unit_combo.currentText()
        if unit_text:
            self.calculator.set_unit_system(unit_text.lower())
            
        # Update Superfat
        self.calculator.set_superfat(self.recipe_settings.superfat_spinbox.value())
        
        # Update Lye Type
        self.calculator.set_lye_type(self.recipe_settings.lye_combo.currentText())
        
        # Update Water
        method_text = self.recipe_settings.water_method_combo.currentText()
        val = self.recipe_settings.water_value_spinbox.value()
        
        method_map = {
            'Water:Lye Ratio': 'ratio',
            'Water % of Oils': 'percent',
            'Lye Concentration': 'concentration'
        }
        method = method_map.get(method_text, 'ratio')
        self.calculator.set_water_calc_method(method, val)
        
        # Update UI elements that depend on settings
        self.update_oils_table_headers()
        self.update_scale_label()

    def on_oil_cell_changed(self, row: int, column: int):
        """Handle inline edits to oils table"""
        if getattr(self, '_suppress_oils_table_signals', False):
            return

        try:
            old_name = self._oils_rows[row]
        except Exception:
            return

        # Name change
        if column == 0:
            new_name_item = self.oils_table.item(row, 0)
            if not new_name_item:
                return
            new_name = new_name_item.text().strip()
            if not new_name:
                return
            # transfer weight to new key
            weight_grams = self.calculator.oils.pop(old_name, 0.0)
            self.calculator.oils[new_name] = weight_grams
            self.update_results()

        # Weight change
        if column == 1:
            weight_item = self.oils_table.item(row, 1)
            if not weight_item:
                return
            try:
                display_value = float(weight_item.text())
            except ValueError:
                return
            # convert from display unit to grams
            grams = self.calculator.convert_to_grams(display_value, self.calculator.unit_system)
            # update the oil weight
            self.calculator.oils[old_name] = grams
            self.update_results()

    def remove_selected_oil(self):
        """Remove selected oil from recipe"""
        row = self.oils_table.currentRow()
        if row >= 0 and row < len(getattr(self, '_oils_rows', [])):
            name = self._oils_rows[row]
            self.calculator.remove_oil(name)
            self.update_results()

    def on_additive_cell_changed(self, row: int, column: int):
        """Handle edits to additives table (name or percent)"""
        if getattr(self, '_suppress_additives_table_signals', False):
            return
        additives = dict(sorted(self.calculator.additives.items()))
        keys = list(additives.keys())
        if row < 0 or row >= len(keys):
            return
        name = keys[row]

        # Name edit
        if column == 0:
            item = self.additives_table.item(row, 0)
            if not item:
                return
            new_name = item.text().strip()
            if not new_name:
                return
            # transfer value
            val = self.calculator.additives.pop(name, 0.0)
            self.calculator.additives[new_name] = val
            self.update_results()

        # Amount edit (treat as weight in current unit)
        if column == 1:
            item = self.additives_table.item(row, 1)
            if not item:
                return
            try:
                display_val = float(item.text())
            except ValueError:
                return
            grams = self.calculator.convert_to_grams(display_val, self.calculator.unit_system)
            # update additive grams for that key
            self.calculator.additives[name] = grams
            self.update_results()

    def remove_selected_additive(self):
        """Remove selected additive"""
        row = self.additives_table.currentRow()
        additives = dict(sorted(self.calculator.additives.items()))
        keys = list(additives.keys())
        if row >= 0 and row < len(keys):
            name = keys[row]
            self.calculator.remove_additive(name)
            self.update_results()
            
    def open_ingredient_editor(self):
        """Open the custom ingredient editor dialog"""
        from src.ui.ingredient_editor import IngredientEditorDialog
        dialog = IngredientEditorDialog(self)
        dialog.exec()
        
        # Refresh lists in UI widgets
        self.oil_input_widget.refresh_oils()
        self.additive_widget.refresh_additives()
        if hasattr(self, 'inventory_widget'):
            self.inventory_widget.refresh_ingredients()
    
    @staticmethod
    def _show_recipe_name_dialog(title: str, default: str = "") -> tuple:
        """Show dialog to get recipe name"""
        from PyQt6.QtWidgets import QInputDialog
        return QInputDialog.getText(None, title, "Recipe name:", text=default)
