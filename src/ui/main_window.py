"""Main application window for Fire & Ice Apothecary Soap Calculator."""

# 1. Standard Library

# 2. Third-Party (PyQt6)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QPushButton,
    )
from matplotlib.table import table

# 3. Local Logic/Controller
from src.logic.recipe_controller import RecipeController
from .views.manager_view import RecipeManagementWidget
# 4. Core Data/Models
from src.models import Recipe, RecipeManager, SoapCalculator
from src.models.batch_manager import BatchManager
from src.models.cost_manager import CostManager
from .theme_manager import ThemeManager
# 5. UI Components (Relative imports)
from .batch_history import BatchHistoryWidget
from .tabs.business_tab import ProfitAnalysisWidget
from .tabs.inventory_tab import InventoryCostWidget
from .tabs.mold_volume_tab import MoldVolumeWidget
from .tabs.fatty_acid_tab import FABreakdownWidget
from .tabs.report_tab import RecipeReportWidget
from .tabs.settings_tab import SettingsWidget
from .tabs.recipe_tab import RecipeTab

#LOGGER
from src.utils.logger import log

#Exfoliant
from src.ui.skincare_ingredients import is_exfoliant


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
            super().__init__()
            # 0. Initialize the Guard FIRST
            self._is_refreshing = False
            self._suppress_oils_table_signals = False
            self._suppress_additives_table_signals = False

            self.setWindowTitle("Fire & Ice Apothecary - Soap Calculator")
            self.setGeometry(100, 100, 1400, 900)
            self.showMaximized()

            # 1. INITIALIZE BRAINS
            self.calculator = SoapCalculator()
            self.recipe_manager = RecipeManager("recipes")
            self.cost_manager = CostManager()
            self.batch_manager = BatchManager()
            self.current_recipe = Recipe()
            self._settings = QSettings("FireAndIceApothecary", "SoapCalc")
            self.controller = RecipeController(self, self.calculator, self.cost_manager, self.recipe_manager)
            # 2. INITIALIZE CONTROLLER
            self.manager_widget = RecipeManagementWidget(self.recipe_manager)
            # Theme Manager
            ThemeManager.apply(self)

            # 3. CREATE THE UI
            self.setup_ui()
            self.controller = RecipeController(self, self.calculator, self.cost_manager, self.recipe_manager)
            # 4. BRIDGING: Map Tab variables to MainWindow
            self.recipe_settings = self.recipe_tab.recipe_settings
            self.oil_input_widget = self.recipe_tab.oil_input_widget
            self.oils_table = self.recipe_tab.oils_table
            self.additive_widget = self.recipe_tab.additive_widget
            self.additives_table = self.recipe_tab.additives_table
            self.fragrance_widget = self.recipe_tab.fragrance_widget
            self.results_widget = self.recipe_tab.results_widget
            self.product_type_combo = self.recipe_tab.product_type_combo
            self.scale_label = self.recipe_tab.scale_label
            self.scale_spinbox = self.recipe_tab.scale_spinbox

            # 5. SAFE STARTUP SEQUENCE
            # First: Connect the wires
            self.connect_signals()

            # Second: Mute the entire Window so load_preferences doesn't trigger signals
            self.blockSignals(True)
            try:
                self.load_preferences()
            finally:
                # Third: Unmute the Window
                self.blockSignals(False)

            # Fourth: Perform the ONE AND ONLY initial calculation refresh
            self.update_results()

    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setStyleSheet(
            """
    QMainWindow {
        background-color: #1e1e1e; /* Dark slate background */
    }
    QLabel {
        color: #ffffff; /* White text */
    }
    QTabWidget::pane {
        border: 1px solid #444;
        background: #252526;
    }
    QTabBar::tab {
        background: #333;
        color: #ccc;
        padding: 10px;
        border: 1px solid #444;
    }
    QTabBar::tab:selected {
        background: #00BFFF; /* Ice Blue for active tab */
        color: black;
        font-weight: bold;
    }

    QTableWidget {
    background-color: #2b2b2b;
    alternate-background-color: #353535;
    gridline-color: #444;
    color: #00BFFF; /* Ice blue text for ingredients */
    }

    QHeaderView::section {
    background-color: #444;
    color: white;
    font-weight: bold;
}
"""
        )
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Title
        # title = QLabel("Fire & Ice Apothecary")
        title = QLabel(
            '<span style="color: #FF4500;">Fire</span> & <span style="color: #00BFFF;">Ice</span> Apothecary'
        )
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # Create tabs
        tabs = QTabWidget()

        # Recipe Tab
        self.recipe_tab = RecipeTab(self.calculator, self.cost_manager, self.controller)
        tabs.addTab(self.recipe_tab, "Recipe Calculator")

        # Notes Tab
        # Create the Manager View (The Library)
        self.manager_widget = RecipeManagementWidget(self.recipe_manager)
        tabs.addTab(self.manager_widget, "Manage Recipes")

        # View/Print Tab
        self.print_tab = self.create_print_tab()
        tabs.addTab(self.print_tab, "View / Print")

        # Mold Volume Tab
        self.mold_tab = self.create_mold_tab()
        tabs.addTab(self.mold_tab, "Mold Volume")

        # Inventory/Cost Tab
        self.inventory_tab = self.create_inventory_tab()
        tabs.addTab(self.inventory_tab, "Inventory/Cost")

        # Business/Profit Tab
        self.profit_tab = self.create_profit_tab()
        tabs.addTab(self.profit_tab, "Business / Profit")

        # Batch History Tab
        self.batch_tab = self.create_batch_tab()
        tabs.addTab(self.batch_tab, "Batch Log")

        # FA Breakdown Tab
        #fa_tab = self.create_fa_tab()
        #tabs.addTab(fa_tab, "Fatty Acid Breakdown")

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

    #Tab Creation Methods
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.settings_widget = SettingsWidget(self.calculator)
        layout.addWidget(self.settings_widget)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_mold_tab(self):
        """Create the mold volume calculator tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        self.mold_widget = MoldVolumeWidget(self.calculator)
        layout.addWidget(self.mold_widget)
        tab.setLayout(layout)
        return tab

    #def create_fa_tab(self):
        #"""Create the fatty-acid breakdown tab"""
        #tab = QWidget()
        #layout = QVBoxLayout()
        #self.fa_widget = FABreakdownWidget(self.calculator)
        #layout.addWidget(self.fa_widget)
        #tab.setLayout(layout)
        #return tab

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

    def create_profit_tab(self):
        """Create the business profit analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        self.profit_widget = ProfitAnalysisWidget()
        layout.addWidget(self.profit_widget)
        tab.setLayout(layout)
        return tab

    def create_batch_tab(self):
        """Create the batch history tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        self.batch_widget = BatchHistoryWidget(self.batch_manager)
        layout.addWidget(self.batch_widget)
        tab.setLayout(layout)
        return tab

    # --- Signal Handling ---
    def connect_signals(self):
            """Final Professional Refactor - Signal Routing"""
            # Section 1: UI References (Shorthand for internal use)
            self.oil_input = self.recipe_tab.oil_input_widget
            self.oils_table = self.recipe_tab.oils_table
            self.additive_input = self.recipe_tab.additive_widget
            self.additives_table = self.recipe_tab.additives_table

            # Section 2: Master Refresh Logic
            # These ensure the math updates whenever an ingredient or setting changes
            self.oil_input.oil_added.connect(self.on_recipe_modified)
            self.additive_input.additive_added.connect(self.on_recipe_modified)
            self.recipe_tab.recipe_settings.parameters_changed.connect(self.on_recipe_modified)
            self.inventory_widget.costs_changed.connect(self.on_recipe_modified)

            # Section 3: Specialized Data Handling
            # Cell edits are sent to the controller to validate numbers (g vs %)
            self.oils_table.cellChanged.connect(self.controller.on_oil_cell_changed)
            self.additives_table.cellChanged.connect(self.controller.on_additive_cell_changed)

            # Loading from the Library (Manage Recipes Tab)
            self.manager_widget.recipe_selected_signal.connect(self.controller.on_load_clicked)

            # Section 4: Global App State (Settings & Units)
            self.settings_widget.unit_text_changed.connect(self.recipe_tab.on_unit_changed)
            self.settings_widget.unit_text_changed.connect(self.update_scale_label)
            self.settings_widget.unit_text_changed.connect(self.update_oils_table_headers)
            self.settings_widget.settings_changed.connect(self.on_settings_modified)

            # Section 5: Buttons (The Action Center)
            self.recipe_tab.new_btn.clicked.connect(self.on_new_clicked)
            self.recipe_tab.save_btn.clicked.connect(self.controller.perform_save) # Direct to the save logic
            self.recipe_tab.load_btn.clicked.connect(self.controller.on_load_clicked) # Triggers file dialog
            self.recipe_tab.scale_btn.clicked.connect(self.controller.on_scale_clicked)
            self.recipe_tab.log_btn.clicked.connect(self.log_batch)

    def on_tab_changed(self, index):
        """Handle tab changes"""
        # If switching to Print tab (index check or widget check)
        if self.tabs.widget(index) == self.print_tab:
            notes = self.recipe_tab.notes_widget.get_notes()

            self.report_widget.refresh_report(
                self.current_recipe.name or "Unsaved Recipe", notes
            )
        # Refresh fragrance list when switching to recipe tab (in case inventory changed)
        if index == 0:  # Recipe Tab
            if hasattr(self, "fragrance_widget"):
                self.fragrance_widget.refresh_ingredients()
            # Refresh oils in case a master batch was created
            if hasattr(self, "oil_input_widget"):
                self.oil_input_widget.refresh_oils()

        # Refresh batch list
        if self.tabs.widget(index) == self.batch_tab:
            self.batch_widget.refresh_table()

    def on_product_type_changed(self, text):
        """Handle product type change (Soap vs Skincare)"""
        is_soap = "Soap" in text
        is_scrub = "Body Scrub" in text

        # 1. Toggle Recipe Parameters (Lye, Water, Superfat)
        if hasattr(self, "recipe_settings"):
            self.recipe_settings.setVisible(is_soap)

        # The widgets are now on the stacked widget, so their visibility is handled automatically.
        # We just need to set the mode for the additive widget when the product type changes.
        if hasattr(self, "additive_widget"):
            self.additive_widget.set_mode("soap" if is_soap else "skincare")
        # 2. Update Input Labels and middle UI stack
        if hasattr(self, "oil_input_widget"):
            self.oil_input_widget.set_mode("soap" if is_soap else "skincare")
        self.middle_stack.setCurrentIndex(1 if is_scrub else 0)

        # 3. Update Results Widget
        if hasattr(self, "results_widget"):
            if is_scrub:
                mode = "body_scrub"
            elif is_soap:
                mode = "soap"
            else:
                mode = "skincare"
            self.results_widget.set_mode(mode)
            self.update_results()
        self.update_scale_label()
        self.update_additives_table()

    # --- Theme & Appearance ---
    def update_theme_from_settings(self):
        theme_name = self.settings_widget.theme_combo.currentText()
        ThemeManager.apply(self, theme_name)

    # --- Table Updates ---
    def update_input_units(self):
        """Update input widgets with new unit system"""
        unit = self.calculator.unit_system
        if hasattr(self, "oil_input_widget"):
            self.oil_input_widget.set_unit_system(unit)
        if hasattr(self, "additive_widget"):
            self.additive_widget.set_unit_system(unit)
        if hasattr(self, "scrub_oils_input"):
            self.scrub_oils_input.set_unit_system(unit)
        if hasattr(self, "scrub_exfoliants_input"):
            self.scrub_exfoliants_input.set_unit_system(unit)
        if hasattr(self, "scrub_other_additives_input"):
            self.scrub_other_additives_input.set_unit_system(unit)

    def update_additives_table(self):
        """Update additives tables based on mode"""
        # 1. Check if we even have a table to update
        if not hasattr(self, "additives_table"):
            return

        # 2. Use the additives signal guard, not the oils one
        self._suppress_additives_table_signals = True

        try:
            additives = self.calculator.additives
            is_scrub = "Body Scrub" in self.product_type_combo.currentText()
            is_soap = "Soap" in self.product_type_combo.currentText()

            if is_scrub:
                # (Your existing scrub logic is fine here...)
                exfoliants = {k: v for k, v in additives.items() if is_exfoliant(k)}
                other_additives = {k: v for k, v in additives.items() if not is_exfoliant(k)}
                self._populate_additive_table(self.scrub_exfoliants_table, exfoliants, is_soap)
                self._populate_additive_table(self.scrub_other_additives_table, other_additives, is_soap)
                self.additives_table.setRowCount(0)
            else:
                self._populate_additive_table(self.additives_table, additives, is_soap)

        except Exception as e:
            print(f"Error updating additives table: {e}")
        finally:
            self._suppress_additives_table_signals = False
    def _populate_additive_table(
        self, table: QTableWidget, additives: dict, is_soap: bool
    ):
        """Helper to fill an additives table with data."""
        self._suppress_additives_table_signals = True
        unit_abbr = self.calculator.get_unit_abbreviation()
        is_skincare = not is_soap

        if is_skincare:
            header_pct = "% of Batch"
        else:
            header_pct = "% of Oils"

        table.setHorizontalHeaderLabels(
            [
                "Additive",
                f"Amount ({unit_abbr})",
                header_pct,
                "Water Replacement",
                "Cost",
            ]
        )
        table.setColumnHidden(3, not is_soap)
        table.setRowCount(len(additives))
        from src.data.additives import get_additive_info

        if is_skincare:
            total_weight_for_pct = sum(self.calculator.oils.values()) + sum(
                self.calculator.additives.values()
            )
        else:  # is_soap
            total_weight_for_pct = self.calculator.get_total_oil_weight()

        for row, (name, grams) in enumerate(sorted(additives.items())):
            display_amount = self.calculator.convert_weight(
                grams, self.calculator.unit_system
            )
            percentage = (
                (grams / total_weight_for_pct * 100)
                if total_weight_for_pct > 0
                else 0.0
            )
            cost_per_g = self.cost_manager.get_cost_per_gram(name)
            cost = grams * cost_per_g
            has_stock = self.cost_manager.has_sufficient_stock(name, grams)
            text_color = QColor("#e0e0e0") if has_stock else QColor("#ff5252")

            name_item = QTableWidgetItem(name)
            amt_item = QTableWidgetItem(f"{display_amount:.2f}")
            pct_item = QTableWidgetItem(f"{percentage:.2f}")
            info = get_additive_info(name)
            repl_item = QTableWidgetItem(
                "Yes" if info.get("is_water_replacement") else "No"
            )
            cost_item = QTableWidgetItem(f"${cost:.2f}")

            table.setItem(row, 0, name_item)
            table.setItem(row, 1, amt_item)
            table.setItem(row, 2, pct_item)
            table.setItem(row, 3, repl_item)
            table.setItem(row, 4, cost_item)

            for col in range(5):
                table.item(row, col).setForeground(text_color)

        self._suppress_additives_table_signals = False

    def update_oils_table(self):
        """Syncs the physical table with the data in self.calculator"""
        table = self.oils_table

        self._suppress_oils_table_signals = True


        try:
            # Point DIRECTLY to the tab's table to ensure no ghosting
            table = self.recipe_tab.oils_table

            # FORCE column count and headers if they are missing
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["Oil Name", "Weight", "%","Cost", "Action"])
            unit = self.calculator.unit_system
            table.setRowCount(0)

            self._oils_rows = list(self.calculator.oils.keys())
            total_weight = self.calculator.get_total_oil_weight()
            #unit = self.calculator.unit_system

            for row, name in enumerate(self._oils_rows):
                table.insertRow(row)

                weight_grams = self.calculator.oils.get(name, 0)
                display_weight = self.calculator.convert_from_grams(weight_grams, unit)
                percentage = (weight_grams / total_weight * 100) if total_weight > 0 else 0
                cost_per_g = self.cost_manager.get_cost_per_gram(name)
                total_cost = weight_grams * cost_per_g

                # Use str(name) and f-strings to ensure we are passing strings to the table
                table.setItem(row, 0, QTableWidgetItem(str(name)))
                table.setItem(row, 1, QTableWidgetItem(f"{display_weight:.2f}"))
                table.setItem(row, 2, QTableWidgetItem(f"{percentage:.2f}"))
                table.setItem(row, 3, QTableWidgetItem(f"${total_cost:.2f}"))
                delete_btn = QPushButton("Remove")
                # Use a specific style so we know if it's drawing
                delete_btn.setStyleSheet("background-color: #444; color: white;")
                delete_btn.clicked.connect(lambda _, n=name: self.handle_remove_oil_by_name(n))
                table.setCellWidget(row, 4, delete_btn)

            # Force the UI to repaint
            table.viewport().update()

        finally:
            self._suppress_oils_table_signals = False
            self.recipe_tab.oils_table.setMinimumHeight(200) # Ensure it's not collapsed
            self.recipe_tab.oils_table.update()             # Force a repaint
            self.recipe_tab.oils_table.setVisible(True)      # Just in case


    def update_oils_table_headers(self):
        """Update table headers with current unit"""
        self.recipe_settings = self.recipe_tab.recipe_settings
        self.oil_input_widget = self.recipe_tab.oil_input_widget
        self.oils_table = self.recipe_tab.oils_table
        self.product_type_combo = self.recipe_tab.product_type_combo
        self.middle_stack = self.recipe_tab.middle_stack
        self.results_widget = self.recipe_tab.results_widget
        self.additive_widget = self.recipe_tab.additive_widget
        self.additives_table = self.recipe_tab.additives_table
        unit_abbr = self.calculator.get_unit_abbreviation()
        is_soap = "Soap" in self.product_type_combo.currentText()

        if not is_soap:
            headers = ["Ingredient", f"Weight ({unit_abbr})", "% of Batch", "Cost"]
        else:
            headers = ["Oil Name", f"Weight ({unit_abbr})", "% of Oils", "Cost"]

        if hasattr(self, "oils_table"):
            self.oils_table.setHorizontalHeaderLabels(headers)
        if hasattr(self, "scrub_oils_table"):
            headers[0] = "Oil/Butter"
            self.scrub_oils_table.setHorizontalHeaderLabels(headers)

    # --- Logic & Calculations ---
    def update_scale_label(self):
        """Update scale label with current unit system from the calculator."""
        # Ensure we are referencing the actual UI element from the tab
        if not hasattr(self, "scale_label"):
            self.scale_label = self.recipe_tab.scale_label

        unit_abbr = self.calculator.get_unit_abbreviation()
        product_type = self.product_type_combo.currentText()

        # Determine label text based on mode
        if "Body Scrub" in product_type:
            label_text = "Target Batch Weight"
        else:
            label_text = "Total Oil Weight"

        self.scale_label.setText(f"{label_text} ({unit_abbr}):")

    def get_target_batch_weight(self):
        """Get target batch weight in grams for percentage calculations"""
        self.scale_spinbox = self.recipe_tab.scale_spinbox  # Map it here
        val = self.scale_spinbox.value()
        return self.calculator.convert_to_grams(val, self.calculator.unit_system)

    def on_packaging_cost_sync(self, cost: float):
        """Syncs packaging cost from results widget to profit analysis widget."""
        if hasattr(self, "profit_widget"):
            self.profit_widget.set_packaging_cost(cost)

    def on_mold_weight_calculated(self, grams):
        """Handle weight calculated from mold tab"""
        self.scale_spinbox = self.recipe_tab.scale_spinbox  # Map it here
        val = self.calculator.convert_weight(grams, self.calculator.unit_system)
        self.scale_spinbox.setValue(val)
        # ...
        self.tabs.setCurrentWidget(self.tabs.widget(0))  # Switch to recipe tab
        self.statusBar().showMessage(
            f"Target weight set to {val:.2f} based on mold volume."
        )

    def scale_recipe(self):
        """Scale recipe to new weight"""
        new_target_weight = self.scale_spinbox.value()
        unit_abbr = self.calculator.get_unit_abbreviation()

        is_soap = "Soap" in self.product_type_combo.currentText()

        # For soap, the target is oil weight. For skincare, it's total batch weight.
        if is_soap:
            current_basis = self.calculator.get_total_oil_weight()
        else:  # Skincare
            current_basis = self.calculator.get_total_oil_weight() + sum(
                self.calculator.additives.values()
            )

        if new_target_weight > 0 and current_basis > 0:
            target_basis_grams = self.calculator.convert_to_grams(
                new_target_weight, self.calculator.unit_system
            )
            ratio = target_basis_grams / current_basis

            # Scale oils
            for name, amount in self.calculator.oils.items():
                self.calculator.oils[name] = amount * ratio

            # Scale Additives
            for name, amount in self.calculator.additives.items():
                self.calculator.additives[name] = amount * ratio

            self.update_results()
            self.statusBar().showMessage(
                f"Recipe scaled to {new_target_weight}{unit_abbr}"
            )

    # --- Batch & Recipe Operations ---
    def log_batch(self):
        """Log current recipe as a new batch"""
        if not self.calculator.oils:
            QMessageBox.warning(self, "Error", "Recipe is empty.")
            return

        # Create recipe snapshot
        recipe_data = self.calculator.get_recipe_dict()
        recipe_data["name"] = self.current_recipe.name or "Unsaved Batch"
        notes = ""

        # Check for insufficient stock before deducting
        insufficient_items = []

        for name, weight in self.calculator.oils.items():
            if not self.cost_manager.has_sufficient_stock(name, weight):
                insufficient_items.append(name)
        for name, weight in self.calculator.additives.items():
            if not self.cost_manager.has_sufficient_stock(name, weight):
                insufficient_items.append(name)
        lye_weight = self.calculator.get_lye_weight()
        if not self.cost_manager.has_sufficient_stock(
            self.calculator.lye_type, lye_weight
        ):
            insufficient_items.append(self.calculator.lye_type)

        if insufficient_items:
            QMessageBox.warning(
                self,
                "Insufficient Stock",
                f"Cannot log batch. The following items have insufficient inventory:\n\n{', '.join(insufficient_items)}\n\nPlease update your inventory or adjust the recipe.",
            )
            return

        # Deduct Inventory
        deducted_count = 0
        missing_items = []

        # Helper to deduct
        def process_deduction(name, weight):
            nonlocal deducted_count
            remaining = self.cost_manager.deduct_stock(name, weight)
            if remaining >= 0:
                deducted_count += 1
            else:
                missing_items.append(name)

        # Deduct Oils
        for name, weight in self.calculator.oils.items():
            process_deduction(name, weight)

        # Deduct Additives
        for name, weight in self.calculator.additives.items():
            process_deduction(name, weight)

        # Deduct Lye
        lye_type = self.calculator.lye_type
        lye_weight = self.calculator.get_lye_weight()
        process_deduction(lye_type, lye_weight)

        # Refresh inventory UI if visible
        if hasattr(self, "inventory_widget"):
            self.inventory_widget.refresh_table()
            self.inventory_widget.costs_changed.emit()

        batch = self.batch_manager.create_batch(recipe_data, notes)

        msg = f"Batch logged: Lot {batch['lot_number']}. "
        if deducted_count > 0:
            msg += f"Inventory deducted for {deducted_count} items."
        if missing_items:
            msg += f" Warning: {len(missing_items)} items not in inventory."

        self.statusBar().showMessage(msg)

    def load_recipe(self):
        """Standard file dialog to pick a recipe file."""
        from PyQt6.QtWidgets import QFileDialog

        # This opens the actual Windows file explorer
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Recipe", "recipes", "Recipe files (*.json)"
        )

        # If the user didn't hit cancel, send the path to the loader
        if filepath:
            self.load_recipe_file(filepath)

    def load_recipe_file(self, filepath):
        """Loads data and sets the recipe name from the file."""
        import os
        if not filepath: return

        # Load data into calculator
        self.controller.perform_load(filepath)

        # Set the name from the filename
        recipe_name = os.path.splitext(os.path.basename(filepath))[0]
        self.current_recipe.name = recipe_name

        # Trigger the controller to refresh the UI with the new name
        self.update_results()

        self.statusBar().showMessage(f"Loaded: {recipe_name}")

    # New Recipe Clicked
    def on_new_clicked(self):
        """Create new recipe and clear the interface"""
        # 1. Reset existing calculator state
        self.calculator.oils.clear()
        self.calculator.additives.clear()
        self._oils_rows = []
        self._additives_rows = []
        # We reach into the recipe_tab to find the notes_widget
        self.recipe_tab.notes_widget.set_notes("")

        # 3. Reset the recipe object
        self.current_recipe = Recipe()

        # 4. Reload defaults (this updates results and UI tables)
        self.load_preferences()
        self.update_oils_table()

        log.debug("New recipe initialized with default preferences. Refreshing UI.")
        self.statusBar().showMessage("New recipe created.")


    def load_preferences(self):
            """Load persisted preferences into the calculator and UI."""
            # 1. BRIDGE MAPPING
            self.recipe_settings = self.recipe_tab.recipe_settings
            self.oil_input_widget = self.recipe_tab.oil_input_widget
            self.oils_table = self.recipe_tab.oils_table
            self.results_widget = self.recipe_tab.results_widget
            self.additive_widget = self.recipe_tab.additive_widget
            self.additives_table = self.recipe_tab.additives_table

            # 2. SIGNAL BLOCKING (Deep Block)
            # We need to block the individual widgets, not just the container
            widgets_to_block = []
            if hasattr(self, "settings_widget"):
                widgets_to_block.extend(self.settings_widget.findChildren((QComboBox, QDoubleSpinBox, QSpinBox)))
            if hasattr(self, "recipe_settings"):
                widgets_to_block.extend(self.recipe_settings.findChildren((QComboBox, QDoubleSpinBox, QSpinBox)))

            for w in widgets_to_block:
                w.blockSignals(True)

            try:
                # Unit System (Grams/Ounces)
                unit = self._settings.value("unit_system", "grams")
                combo = self.settings_widget.unit_combo

                # Match the saved unit to the dropdown
                for i in range(combo.count()):
                    if combo.itemText(i).lower() == str(unit).lower():
                        combo.setCurrentIndex(i)
                        break

                # Superfat Percent
                superfat = float(self._settings.value("superfat_percent", 5.0))
                self.recipe_settings.superfat_spinbox.setValue(superfat)

                # Water Calculation Method
                water_method = self._settings.value("water_calc_method", "ratio")
                method_map_rev = {
                    "ratio": "Water:Lye Ratio",
                    "percent": "Water % of Oils",
                    "concentration": "Lye Concentration",
                }
                target_text = method_map_rev.get(water_method, "Water:Lye Ratio")
                w_combo = self.recipe_settings.water_method_combo
                for i in range(w_combo.count()):
                    if w_combo.itemText(i) == target_text:
                        w_combo.setCurrentIndex(i)
                        break

                # Water Values
                w_ratio = float(self._settings.value("water_to_lye_ratio", 2.0))
                w_percent = float(self._settings.value("water_percent", 38.0))
                lye_conc = float(self._settings.value("lye_concentration", 30.0))

                if water_method == "percent":
                    self.recipe_settings.water_value_spinbox.setValue(w_percent)
                elif water_method == "concentration":
                    self.recipe_settings.water_value_spinbox.setValue(lye_conc)
                else:
                    self.recipe_settings.water_value_spinbox.setValue(w_ratio)

                # Lye Type (NaOH/KOH)
                lye_type = self._settings.value("lye_type", "NaOH")
                self.recipe_settings.lye_combo.setCurrentText(lye_type)

                # Theme Accent
                theme = self._settings.value("theme_accent", "Blue")
                self.settings_widget.theme_combo.setCurrentText(theme)

            except (ValueError, TypeError) as e:
                print(f"Error loading preferences: {e}")
            finally:
                # 3. RELEASE SIGNALS (Deep Unblock)
                for w in widgets_to_block:
                    w.blockSignals(False)

            # 4. FINAL SYNC & UI REFRESH
            # Use the logic-safe way to get the unit
            current_unit = self.settings_widget.unit_combo.currentText().lower()
            self.calculator.set_unit_system(current_unit)

            self.sync_settings_to_calculator()
            self.update_input_units()
            self.update_theme_from_settings()
            self.update_scale_label()
            self.update_oils_table()
            self.update_additives_table()

            # This runs the ONE AND ONLY calculation refresh
            #self.update_results()

    def save_preferences(self):
        """Persist current preferences to QSettings."""
        self._settings.setValue("unit_system", self.calculator.unit_system)
        self._settings.setValue(
            "superfat_percent", float(self.calculator.superfat_percent)
        )
        self._settings.setValue("water_calc_method", self.calculator.water_calc_method)
        self._settings.setValue(
            "water_to_lye_ratio", float(self.calculator.water_to_lye_ratio)
        )
        self._settings.setValue("water_percent", float(self.calculator.water_percent))
        self._settings.setValue(
            "lye_concentration", float(self.calculator.lye_concentration)
        )
        self._settings.setValue("lye_type", self.calculator.lye_type)
        self._settings.setValue(
            "theme_accent", self.settings_widget.theme_combo.currentText()
        )

    def sync_settings_to_calculator(self):
        """Ensure calculator is updated from settings widget"""
        self.recipe_settings = self.recipe_tab.recipe_settings
        self.oil_input_widget = self.recipe_tab.oil_input_widget
        self.oils_table = self.recipe_tab.oils_table
        self.product_type_combo = self.recipe_tab.product_type_combo
        self.middle_stack = self.recipe_tab.middle_stack
        self.results_widget = self.recipe_tab.results_widget
        self.additive_widget = self.recipe_tab.additive_widget
        self.additives_table = self.recipe_tab.additives_table
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
            "Water:Lye Ratio": "ratio",
            "Water % of Oils": "percent",
            "Lye Concentration": "concentration",
        }
        method = method_map.get(method_text, "ratio")
        self.calculator.set_water_calc_method(method, val)

        # Update UI elements that depend on settings
        self.update_oils_table_headers()
        self.update_scale_label()

    def remove_selected_oil(self, table: QTableWidget):
        """Remove selected oil from recipe"""
        row = table.currentRow()
        if row >= 0 and row < len(getattr(self, "_oils_rows", [])):
            name = self._oils_rows[row]
            self.calculator.remove_oil(name)
            self.update_results()

    def handle_remove_oil_by_name(self, name):
            """Specifically for the 'Remove' buttons in the table"""
            # 1. Tell the controller to kill it by name
            self.controller.remove_oil(name)

            # 2. Refresh everything
            self.update_oils_table()
            self.update_results()

    def remove_selected_additive(self, table: QTableWidget):
        """Remove selected additive"""
        row = table.currentRow()

        # Determine which subset of additives this table represents
        is_scrub = "Body Scrub" in self.product_type_combo.currentText()
        is_exfoliant_table = table == getattr(self, "scrub_exfoliants_table", None)

        if is_scrub:
            keys = sorted(
                [
                    k
                    for k, v in self.calculator.additives.items()
                    if (is_exfoliant(k) if is_exfoliant_table else not is_exfoliant(k))
                ]
            )
        else:
            keys = sorted(self.calculator.additives.keys())

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
        if hasattr(self, "inventory_widget"):
            self.inventory_widget.refresh_ingredients()
        if hasattr(self, "scrub_oils_input"):
            self.scrub_oils_input.refresh_oils()
            self.scrub_exfoliants_input.refresh_oils()
            self.scrub_other_additives_input.refresh_oils()

    @staticmethod
    def _show_recipe_name_dialog(title: str, default: str = "") -> tuple:
        """Show dialog to get recipe name"""
        from PyQt6.QtWidgets import QInputDialog

        return QInputDialog.getText(None, title, "Recipe name:", text=default)

    def save_recipe(self):
        self.controller.perform_save()

    def update_results(self):
            # 1. CHECK THE GUARD BEFORE LOGGING ANYTHING
            if self._is_refreshing:
                return

            # 2. LOCK THE DOOR
            self._is_refreshing = True

            try:
                # Now we log, because we know this is the only one running
                log.debug("Starting universal calculation update...")
                self.controller.update_calculations()
            finally:
                # 3. UNLOCK THE DOOR
                self._is_refreshing = False
    #Master Refresh
    def on_settings_modified(self):
        """Checklist for when the unit system or theme changes"""
        log.debug("Master Settings Refresh Triggered")
        self.sync_settings_to_calculator()
        self.update_input_units()
        self.update_theme_from_settings()
        self.update_scale_label()
        self.update_results() # Run math once
        self.update_oils_table()
        self.update_additives_table()
        self.save_preferences()

    def on_recipe_modified(self):
        """Checklist for when ingredients or percentages change"""
        log.debug("Master Recipe Refresh Triggered")
        self.update_results()
        self.update_oils_table()
        self.update_additives_table()
        self.save_preferences()

    def get_current_mode(self):
        """Returns the currently active mode from the UI"""
        return "Soap"