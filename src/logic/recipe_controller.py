import json
import os
from PyQt6.QtWidgets import QInputDialog,QFileDialog
from pathlib import Path
from src.models.recipe import Recipe
from src.utils.logger import log
from ..models.recipe import Recipe, RecipeManager
from src.ui.tabs import  RecipeParametersWidget
from src.models.cost_manager import CostManager

#RecipeController: The Mastermind of Recipe Management
class RecipeController:
    #init
    def __init__(self, view, calculator, cost_manager, recipe_manager):
        self.view = view
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.recipes = recipe_manager

        self.recipe_manager = RecipeManager()
        self.current_recipe = self.view.current_recipe
        self._calculating = False

    #Universal Calculation Update
    def update_calculations(self):
        """Refreshes all math, unit labels, and identity markers in the UI."""
        # 1. Sync the unit from settings
        unit_pref = self.view._settings.value("unit_system", "grams").lower()
        self.calculator.unit_system = unit_pref

        # 2. Get base properties from the model
        results = self.calculator.get_batch_properties()
        results['unit_system_abbr'] = self.calculator.get_unit_abbreviation()

        # 3. Handle Masterbatch Logic
        is_mb = self.view.recipe_tab.recipe_settings.masterbatch_check.isChecked()
        results['is_masterbatch'] = is_mb
        if is_mb:
            target_final = self.view.recipe_tab.recipe_settings.target_conc_spin.value()
            mb_math = self.calculator.calculate_masterbatch_pour(
                target_lye_grams=results['lye_weight'],
                mb_concentration=50.0,
                final_target_conc=target_final
            )
            results.update(mb_math)

        # 4. NEW: Calculate Costs & Yield (Moved from UI)
        total_cost = 0.0
        if self.cost_manager:
            # Calculate Oil costs
            for name, weight in self.calculator.oils.items():
                total_cost += (weight * self.cost_manager.get_cost_per_gram(name))
            # Calculate Additive costs
            for name, weight in self.calculator.additives.items():
                total_cost += (weight * self.cost_manager.get_cost_per_gram(name))

        # Calculate Packaging
        pkg_val = self.view.recipe_tab.results_widget.ypacking_cost_spin.value()
        # Your specific formula: 10 units minus a 0.1 adjustment
        packaging_total = pkg_val

        results['packaging_cost'] = packaging_total
        results['total_batch_cost'] = total_cost + packaging_total

        # Calculate Yield
        total_weight = results.get('total_batch_weight', 0.0)
        container_size = self.view.recipe_tab.results_widget.bar_size_spin.value()
        results['yield'] = total_weight / container_size if container_size > 0 else 0.0

        # 5. Update the UI
        self.view.recipe_tab.results_widget.update_display(results)

        # 6. Sync UI Labels (Name and Scaling)
        recipe_name = self.view.current_recipe.name or "New Recipe"
        if hasattr(self.view.recipe_tab.results_widget, 'recipe_name_label'):
            self.view.recipe_tab.results_widget.recipe_name_label.setText(recipe_name)

        if hasattr(self.view, 'update_scale_label'):
            self.view.update_scale_label()

        # 7. Refresh Tables
        self.view._suppress_oils_table_signals = True
        self.view.update_oils_table()
        self.view.update_additives_table()
        self.view._suppress_oils_table_signals = False

    #Perform Save with Manual JSON Patching
    def perform_save(self):
        """Saves recipe with manual JSON additive patching and updated UI paths."""
        name, ok = QInputDialog.getText(
            self.view, "Save Recipe", "Recipe Name:", text=self.view.current_recipe.name
        )
        if ok and name:
            self.view.current_recipe.name = name
            # Sync calculator state to recipe object
            r = self.view.current_recipe
            r.oils = self.calculator.oils.copy()
            r.additives = self.calculator.additives.copy()
            r.lye_type = self.calculator.lye_type
            r.water_calc_method = self.calculator.water_calc_method
            r.water_to_lye_ratio = self.calculator.water_to_lye_ratio
            r.water_percent = self.calculator.water_percent
            r.lye_concentration = self.calculator.lye_concentration
            r.superfat_percent = self.calculator.superfat_percent

            # The manager saves the base file
            filepath = self.recipe_manager.save_recipe(r)

            if filepath:
                try:
                    # RE-OPEN to patch in the extra bits manually
                    with open(filepath, "r") as f:
                        data = json.load(f)

                    # UPDATE: Using the new nested path for notes
                    data["additives"] = self.calculator.additives
                    data["notes"] = self.view.recipe_tab.notes_widget.get_notes()  # <--- FIXED PATH

                    temp_path = f"{filepath}.tmp"
                    with open(temp_path, "w") as f:
                        json.dump(data, f, indent=4)
                    os.replace(temp_path, filepath)

                    # Refresh the manager list so the new file shows up immediately
                    self.view.manager_widget.refresh_recipe_list()

                except (json.JSONDecodeError, IOError, OSError) as e:
                    log.error(f"Manual JSON Save Error: {e}")
                    if os.path.exists(f"{filepath}.tmp"):
                        try:
                            os.remove(f"{filepath}.tmp")
                        except OSError:
                            pass

            self.update_calculations()
    #Perform Load with UI Signal Blocking
    def perform_load(self, filepath):
        """Loads recipe"""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            loaded_recipe = Recipe.from_dict(data)

            # BLOCK UI SIGNALS
            self.view.blockSignals(True)

            try:
                # 1. Update the reference
                self.view.current_recipe = loaded_recipe

                # 2. Update the calculator state
                self.calculator.oils = loaded_recipe.oils.copy()
                self.calculator.additives = data.get("additives", {}).copy()
                self.calculator.water_calc_method = loaded_recipe.water_calc_method
                self.calculator.water_to_lye_ratio = loaded_recipe.water_to_lye_ratio
                self.calculator.water_percent = loaded_recipe.water_percent
                self.calculator.lye_concentration = loaded_recipe.lye_concentration
                self.calculator.lye_type = loaded_recipe.lye_type
                self.calculator.superfat_percent = loaded_recipe.superfat_percent

                # 3. UPDATE: Push notes into the NEW widget location
                notes = data.get("notes", "")
                self.view.recipe_tab.notes_widget.set_notes(notes) # <--- FIXED PATH

                # 4. Refresh visuals
                self.view.update_oils_table()
                #used to be self.view.controller.update_calculations()
                self.update_calculations()


            finally:
                self.view.blockSignals(False)

            # Update UI controls to match loaded values
            self.view.recipe_tab.superfat_spinbox.setValue(self.calculator.superfat_percent)
            self.view.recipe_tab.lye_combo.setCurrentText(self.calculator.lye_type)
            method_to_text = {
                "ratio": "Water:Lye Ratio",
                "percent": "Water % of Oils",
                "concentration": "Lye Concentration"
            }
            self.view.recipe_tab.water_method_combo.setCurrentText(method_to_text.get(self.calculator.water_calc_method, "Water:Lye Ratio"))

            log.info(f"Successfully loaded and calculated: {loaded_recipe.name}")

        except Exception as e:
            log.error(f"Load Error: {e}")
    #Oils Table Logic
    def on_oil_cell_changed(self, row, column):
        """Handle inline edits to oils table via the controller"""
        if getattr(self.view, "_suppress_oils_table_signals", False):
                return
        self.view.on_recipe_modified()



        if getattr(self.view, "_suppress_oils_table_signals", False):
            return

        try:
            # Access the row mapping stored in MainWindow
            old_name = self.view._oils_rows[row]
        except IndexError:
            return

        # 1. Handle Name change (Column 0)
        if column == 0:
            item = self.view.recipe_tab.oils_table.item(row, 0)
            if item:
                new_name = item.text().strip()
                if new_name and new_name != old_name:
                    weight_grams = self.calculator.oils.pop(old_name, 0.0)
                    self.calculator.oils[new_name] = weight_grams
                    #self.view.update_results()
                    self.update_calculations()
                    self.view.update_oils_table()
        # 2. Handle Weight change (Column 1)
        elif column == 1:
            item = self.view.recipe_tab.oils_table.item(row, 1)
            if item:
                try:
                    display_value = float(item.text())
                    grams = self.calculator.convert_to_grams(
                        display_value, self.calculator.unit_system
                    )
                    self.calculator.oils[old_name] = grams
                    #self.view.update_results()
                    self.update_calculations()
                    self.view.update_oils_table()
                except ValueError as e:
                    log.warning(f"Invalid weight in oils table row {row}: {e}")

        # 3. Handle Percent change (Column 2)
        elif column == 2:
            item = self.view.recipe_tab.oils_table.item(row, 2)
            if item:
                try:
                    percent = float(item.text())
                    target_grams = self.view.recipe_tab.scale_spinbox.value()
                    if target_grams <= 0:
                        target_grams = self.calculator.get_total_oil_weight()

                    self.calculator.oils[old_name] = target_grams * (percent / 100.0)
                    #self.view.update_results()
                    self.update_calculations()
                    self.view.update_oils_table()
                except ValueError as e:
                    log.warning(f"Invalid percentage in oils table row {row}: {e}")
    #Additives Table Logic
    def on_additive_cell_changed(self, row, column):


        """Handle edits to additives tables via the controller"""
        if getattr(self.view, "_suppress_additives_table_signals", False):
            return

        keys = sorted(self.calculator.additives.keys())
        if row < 0 or row >= len(keys):
            return

        name = keys[row]

        # Process Weight/Amount edit (Column 1)
        if column == 1:
            item = self.view.recipe_tab.additives_table.item(row, 1)
            if item:
                try:
                    display_val = float(item.text())
                    grams = self.calculator.convert_to_grams(
                        display_val, self.calculator.unit_system
                    )
                    self.calculator.additives[name] = grams
                    #self.view.update_results()
                    self.update_calculations()
                except ValueError as e:
                    log.warning(f"Invalid additive amount in row {row}: {e}")
    #Scale Recipe
    def on_scale_clicked(self):
        target_weight = self.view.recipe_tab.scale_spinbox.value()
        # Get the current unit (e.g., 'ounces')
        current_unit = self.calculator.unit_system

        if target_weight > 0:
            # Convert the user's input (oz/lbs) into grams for the calculator
            target_in_grams = self.calculator.convert_to_grams(target_weight, current_unit)

            self.calculator.scale_recipe(target_in_grams)
            self.view.on_recipe_modified()
    #Save Recipe
    def on_save_clicked(self):
            log.info("Save recipe initiated using RecipeManager")
            path, _ = QFileDialog.getSaveFileName(self.view, "Save Recipe", "recipes", "JSON Files (*.json)")

            if path:
                try:
                    filename_stem = Path(path).stem

                    # 1. Get the data directly from the calculator (already a dict)
                    data = self.calculator.get_recipe_data()

                    # 2. Update the name in the dictionary
                    data['name'] = filename_stem

                    # 3. Save using the manager
                    manager = RecipeManager()
                    manager.save_recipe(data, filename_stem)

                    # 4. Update the name in the UI/Model safely
                    if hasattr(self.view.current_recipe, 'name'):
                        self.view.current_recipe.name = filename_stem
                    elif isinstance(self.view.current_recipe, dict):
                        self.view.current_recipe['name'] = filename_stem

                    log.info(f"Successfully saved {filename_stem}")

                except Exception as e:
                    # This will now tell us EXACTLY which line is failing if it happens again
                    import traceback
                    log.error(f"Save failed: {str(e)}")
                    log.error(traceback.format_exc())
    #Load Recipe
    def on_load_clicked(self, filepath=None):
        """
        Handles loading. If filepath is provided (from Library), use it.
        If not (from Button), open the File Dialog.
        """
        log.info("Load recipe initiated")

        # If no filepath was passed (meaning the 'Load' button was clicked)
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self.view, "Open Recipe", "recipes", "JSON Files (*.json)"
            )

        if filepath:
            # Pass the work to perform_load to keep this clean
            self.perform_load(filepath)