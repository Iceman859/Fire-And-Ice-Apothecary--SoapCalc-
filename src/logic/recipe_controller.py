import json
import os
from PyQt6.QtWidgets import QInputDialog, QFileDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from src.models.recipe import Recipe
from src.utils.logger import log


from src.utils.logger import log

class RecipeController:
    def __init__(self, view, calculator, cost_manager, recipe_manager, batch_manager):
        """Restored full signature to match MainWindow initialization."""
        self.view = view
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.recipe_manager = recipe_manager
        self.batch_manager = batch_manager

    def update_calculations(self):
        """Main calculation engine. Pulls from UI, runs math, pushes to UI."""
        try:
            # 1. Sync settings from UI to Calculator
            settings = self.view.recipe_tab.recipe_settings

            # Sync Unit System from Model to Calculator
            unit_system = getattr(self.view.recipe_model, 'unit_system', 'grams')
            self.calculator.set_unit_system(unit_system)

            # Superfat
            sf = settings.superfat_spinbox.value()
            self.calculator.set_superfat(sf)

            # Lye Type
            self.calculator.set_lye_type(settings.lye_combo.currentText())

            # Water calculation method
            method_map = {
                "Water:Lye Ratio": "ratio",
                "Water % of Oils": "percent",
                "Lye Concentration": "concentration"
            }
            method_text = settings.water_method_combo.currentText()
            method_key = method_map.get(method_text, "ratio")
            method_val = settings.water_value_spinbox.value()
            self.calculator.set_water_calc_method(method_key, method_val)

            # Masterbatch sync
            is_mb = settings.masterbatch_check.isChecked()
            if hasattr(self.calculator, 'use_masterbatch'):
                self.calculator.use_masterbatch = is_mb

            # 2. CRITICAL: Force Calculator Refresh
            # This ensures that if we just loaded a recipe, the calculator knows
            # it has oils before we ask for properties.
            if hasattr(self.calculator, '_calculate_batch'):
                self.calculator._calculate_batch()

            # 3. Perform math in the Calculator
            results = self.calculator.get_batch_properties()

            # 4. MANUALLY DETERMINE CONVERSION (To match RecipeTableModel exactly)
            if unit_system == "ounces":
                abbr = "oz"
                conv = 28.3495231
            elif unit_system == "pounds":
                abbr = "lb"
                conv = 453.592
            else:
                abbr = "g"
                conv = 1.0

            # 5. Calculate Financials directly from current oils
            # This bypasses any stale data in the results dictionary
            total_cost = 0.0
            total_oil_weight_g = 0.0

            for oil_name, weight_g in self.calculator.oils.items():
                total_oil_weight_g += weight_g
                if self.cost_manager:
                    cost_per_g = self.cost_manager.get_cost_per_gram(oil_name)
                    total_cost += cost_per_g * weight_g

            # 6. MAP DATA TO UI
            def get_grams(key_base, fallback_val=0.0):
                # Try specific gram key, then base key
                val = results.get(f"{key_base}_grams")
                if val is None:
                    val = results.get(key_base)
                return float(val) if val is not None else fallback_val

            # If total_oil_weight_g is 0 but calculator has oils, use our manual sum
            oil_weight_to_use = get_grams('total_oil_weight', total_oil_weight_g)
            if oil_weight_to_use == 0 and total_oil_weight_g > 0:
                oil_weight_to_use = total_oil_weight_g

            ui_data = {
                'unit_system_abbr': abbr,
                'is_masterbatch': is_mb,

                'total_oil_weight': oil_weight_to_use / conv,
                'water_weight': get_grams('water_weight') / conv,
                'lye_weight': get_grams('lye_weight') / conv,
                'total_batch_weight': get_grams('total_batch_weight') / conv,
                'additional_water': get_grams('additional_water') / conv,

                'total_batch_cost': total_cost,
                'est_yield': 0.0,
                'cost_per_unit': 0.0,

                'mb_liquid_pour': get_grams('mb_liquid_pour') / conv,
                'extra_water_to_add': get_grams('extra_water_to_add') / conv
            }

            # 7. Yield & Unit Cost Calculation
            results_widget = self.view.recipe_tab.results_widget
            bar_size = results_widget.bar_size_spin.value()
            pkg_cost = results_widget.pkg_cost_spin.value()

            if bar_size > 0:
                ui_data['est_yield'] = ui_data['total_batch_weight'] / bar_size
                if ui_data['est_yield'] > 0:
                    ui_data['cost_per_unit'] = (total_cost / ui_data['est_yield']) + pkg_cost

            # 8. Push to Results Widget
            results_widget.update_display(ui_data)

            # 9. Solution Warning
            conc = self.calculator.lye_concentration
            # Ensure it's in percentage format (0.33 -> 33)
            if conc < 1.0:
                conc *= 100

            if hasattr(self.view.recipe_tab, 'update_solution_warning'):
                self.view.recipe_tab.update_solution_warning(conc)

        except Exception as e:
            log.error(f"Error in update_calculations: {e}")

    def refresh_additives_table(self):
        """Manually populates the additive QTableWidget from the calculator data."""
        if not hasattr(self.view.recipe_tab, 'additives_table'):
            return

        table = self.view.recipe_tab.additives_table
        table.setRowCount(0)

        unit = self.calculator.unit_system
        conv = 28.3495231

        for name, weight_g in self.calculator.additives.items():
            row = table.rowCount()
            table.insertRow(row)

            # Name
            table.setItem(row, 0, QTableWidgetItem(name))

            # Weight Conversion
            if unit == "ounces":
                display_wt = f"{weight_g / conv:.2f}"
                display_unit = "oz"
            elif unit == "pounds":
                display_wt = f"{(weight_g / conv) / 16:.3f}"
                display_unit = "lbs"
            else:
                display_wt = f"{weight_g:.2f}"
                display_unit = "g"

            table.setItem(row, 1, QTableWidgetItem(display_wt))
            table.setItem(row, 2, QTableWidgetItem(display_unit))

            # Cost
            cost_per_g = self.cost_manager.get_cost_per_gram(name)
            cost = cost_per_g * weight_g
            table.setItem(row, 3, QTableWidgetItem(f"${cost:.2f}"))

    def on_new_clicked(self):
        """Resets the state for a brand new recipe."""
        self.calculator.oils.clear()
        self.calculator.additives.clear()
        self.view.recipe_tab.notes_widget.set_notes("")
        self.view.current_recipe = Recipe()
        self.view.current_recipe.name = "New Recipe"

        unit_pref = self.view._settings.value("unit_system", "grams").lower()
        conv = 28.3495231

        if unit_pref == "ounces":
            self.calculator.total_batch_weight = 32.0 * conv
        elif unit_pref == "pounds":
            self.calculator.total_batch_weight = 2.0 * 16 * conv
        else:
            self.calculator.total_batch_weight = 1000.0

        self.update_calculations()
        self.view.statusBar().showMessage("New recipe created.")

    def on_scale_clicked(self):
        """Scales the recipe based on the target weight in the UI."""
        target_weight = self.view.recipe_tab.scale_spinbox.value()
        unit_sys = self.calculator.unit_system
        current_oil_total = self.calculator.get_total_oil_weight()

        if target_weight > 0 and current_oil_total > 0:
            conv = 28.3495231
            target_grams = target_weight
            if unit_sys == "ounces":
                target_grams = target_weight * conv
            elif unit_sys == "pounds":
                target_grams = (target_weight * 16) * conv

            ratio = target_grams / current_oil_total

            # Scale Oils
            for name in self.calculator.oils:
                self.calculator.oils[name] *= ratio

            # Scale Additives proportionally
            for name in self.calculator.additives:
                self.calculator.additives[name] *= ratio

            self.update_calculations()
            self.view.statusBar().showMessage(f"Scaled oils to {target_weight} {self.calculator.get_unit_abbreviation()}")

    def log_batch(self):
        """Deducts inventory and saves to batch history."""
        if not self.calculator.oils:
            QMessageBox.warning(self.view, "Error", "Cannot log an empty recipe.")
            return

        if not self.batch_manager:
            log.error("Batch Manager not provided to Controller.")
            return

        insufficient = []
        for name, weight in {**self.calculator.oils, **self.calculator.additives}.items():
            if not self.cost_manager.has_sufficient_stock(name, weight):
                insufficient.append(name)

        lye_w = self.calculator.get_lye_weight()
        if not self.cost_manager.has_sufficient_stock(self.calculator.lye_type, lye_w):
            insufficient.append(self.calculator.lye_type)

        if insufficient:
            QMessageBox.warning(self.view, "Stock Warning", f"Low stock on: {', '.join(insufficient)}")
            return

        for name, weight in {**self.calculator.oils, **self.calculator.additives}.items():
            self.cost_manager.deduct_stock(name, weight)
        self.cost_manager.deduct_stock(self.calculator.lye_type, lye_w)

        recipe_data = self.calculator.get_recipe_dict()
        recipe_data["name"] = self.view.current_recipe.name or "Unsaved Batch"
        batch = self.batch_manager.create_batch(recipe_data, self.view.recipe_tab.notes_widget.get_notes())

        self.view.statusBar().showMessage(f"Batch Logged: Lot {batch['lot_number']}")
        if hasattr(self.view, 'inventory_widget'):
            self.view.inventory_widget.refresh_table()

    def perform_save(self):
        """Logic for saving the recipe to a JSON file."""
        name, ok = QInputDialog.getText(self.view, "Save", "Recipe Name:", text=self.view.current_recipe.name)
        if ok and name:
            self.view.current_recipe.name = name
            self.view.current_recipe.oils = self.calculator.oils.copy()
            self.view.current_recipe.additives = self.calculator.additives.copy()
            self.view.current_recipe.notes = self.view.recipe_tab.notes_widget.get_notes()

            path = self.recipe_manager.save_recipe(self.view.current_recipe)
            if path:
                self.view.statusBar().showMessage(f"Saved to {os.path.basename(path)}")
                self.view.manager_widget.refresh_recipe_list()

    def perform_load(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            loaded = Recipe.from_dict(data)
            # ... name logic ...

            # 1. Update the underlying data
            self.calculator.oils = loaded.oils.copy()
            self.calculator.additives = data.get("additives", {}).copy()
            self.view.current_recipe = loaded

            # 2. IMPORTANT: Tell the UI the table has changed
            if hasattr(self.view, 'recipe_model'):
                self.view.recipe_model.refresh()

            # 3. Now run the math (it will see the new rows)
            self.update_calculations()
            self.view.statusBar().showMessage(f"Loaded {loaded.name}")
        except Exception as e:
            log.error(f"Failed to load recipe: {e}")

    def on_load_clicked(self, filepath=None):
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(self.view, "Load Recipe", "recipes", "JSON (*.json)")
        if filepath:
            self.perform_load(filepath)