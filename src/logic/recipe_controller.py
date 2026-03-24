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

            if hasattr(self.view.recipe_tab, 'recipe_model'):
                self.view.recipe_tab.recipe_model.unit_system = self.calculator.unit_system
            # 0. SYNC UNIT SYSTEM TO MODEL AND CALCULATOR
                # Get the current unit from calculator
                unit_system = self.calculator.unit_system

                # Sync to model FIRST
                if hasattr(self.view, 'recipe_model'):
                    self.view.recipe_model.unit_system = unit_system

                # CRITICAL: Ensure calculator knows the current unit system
                # (this is set in MainWindow, but verify it here)
                #log.debug(f"Current unit_system: {unit_system}")

                # 1. Sync settings from UI to Calculator
                settings = self.view.recipe_tab.recipe_settings

            # Sync Unit System
            unit_system = self.calculator.unit_system  # Use calculator's unit directly

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

            # 2. Perform math in the Calculator (this handles unit conversion internally)
            results = self.calculator.get_batch_properties()
            results['unit_system_abbr'] = self.calculator.get_unit_abbreviation()

            # 3. Calculate Financials from current oils
            total_cost = 0.0
            for oil_name, weight_g in self.calculator.oils.items():
                if self.cost_manager:
                    cost_per_g = self.cost_manager.get_cost_per_gram(oil_name)
                    if cost_per_g:
                        total_cost += cost_per_g * weight_g

            # Add additive costs
            for additive_name, weight_g in self.calculator.additives.items():
                if self.cost_manager:
                    cost_per_g = self.cost_manager.get_cost_per_gram(additive_name)
                    if cost_per_g:
                        total_cost += cost_per_g * weight_g

            results['total_batch_cost'] = total_cost

            # 4. Masterbatch Logic (if enabled)
            is_mb = settings.masterbatch_check.isChecked()
            results['is_masterbatch'] = is_mb

            if is_mb:
                results_widget = self.view.recipe_settings
                results_widget.target_conc_spin.setVisible(True)
                results_widget.water_method_combo.setVisible(False)
                results_widget.water_value_spinbox.setVisible(False)


                target_final = settings.target_conc_spin.value()
                lye_grams = results.get('lye_weight', 0)  # This should be the original gram value
                mb_math = self.calculator.calculate_masterbatch_pour(
                    target_lye_grams=lye_grams,
                    mb_concentration=50.0,
                    final_target_conc=target_final
                )
                results.update(mb_math)

            # 5. Yield & Unit Cost Calculation
            results_widget = self.view.results_widget

            bar_size = results_widget.bar_size_spin.value()
            log.debug(f"Bar Size: {bar_size}")

            pkg_cost = results_widget.pkg_cost_spin.value()
            log.debug(f"Package Cost: {pkg_cost}")

            total_batch_weight = results.get('total_batch_weight', 0.0)


            if bar_size > 0:
                # 1. How many bars? (Total Weight / Size of one bar)
                results['est_yield'] = total_batch_weight / bar_size

                if results['est_yield'] > 0:
                    # 2. Add the packaging cost to the big total
                    results['total_batch_cost'] += (pkg_cost * results['est_yield'])

                    # 3. THE MISSING PIECE: Divide the Big Total Cost by the Number of Bars
                    results['cost_per_unit'] = results['total_batch_cost'] / results['est_yield']
                else:
                    results['cost_per_unit'] = 0.0
            else:
                results['est_yield'] = 0.0
                results['cost_per_unit'] = 0.0

            # 6. Push to Results Widget
            results_widget.update_display(results)

            # 7. Update Tables (with model refresh)
            self.view._suppress_oils_table_signals = True
            self.view._suppress_additives_table_signals = True

            try:
                # Refresh the oils table model
                if hasattr(self.view.recipe_tab, 'recipe_model'):
                    self.view.recipe_tab.recipe_model.layoutChanged.emit()

                # Update additives table (still using old method if it exists)
                if hasattr(self.view, 'update_additives_table'):
                    self.view.update_additives_table()
            except Exception as e:
                log.error(f"Table refresh failed: {e}")
            finally:
                # CRITICAL: Re-enable signals
                self.view._suppress_oils_table_signals = False
                self.view._suppress_additives_table_signals = False

                #SEND THE BATSIGNAL
                if hasattr(self.view, 'recipe_model'):
                    self.view.recipe_model.layoutChanged.emit()

        except Exception as e:
            log.error(f"Error in update_calculations: {e}", exc_info=True)

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
            if hasattr(self.view.recipe_tab, 'recipe_model'):
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