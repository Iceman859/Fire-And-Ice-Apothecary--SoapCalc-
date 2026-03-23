import json
import os
from PyQt6.QtWidgets import QInputDialog,QFileDialog
from pathlib import Path
from src.models.recipe import Recipe, RecipeManager
from src.utils.logger import log
from src.ui.tabs import  RecipeParametersWidget, CalculationResultsWidget
from src.models.cost_manager import CostManager

#RecipeController: The Mastermind of Recipe Management
class RecipeController:
    #init
    def __init__(self, view, calculator, cost_manager, recipe_manager):
        self.view = view
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.recipe_manager = recipe_manager
        self.current_recipe = self.view.current_recipe
        self._calculating = False

    #Universal Calculation Update
    def update_calculations(self):
        """Refreshes all math, unit labels, and identity markers with extensive trace logging."""
        #log.debug("Starting Universal Calculation Update")
    # --- STEP 0: SYNC UI TO CALCULATOR (The 'Pull') ---
        # This ensures the calculator has the LATEST info before doing math
        try:
            settings = self.view.recipe_tab.recipe_settings

            # Pull Superfat
            self.calculator.set_superfat(settings.superfat_spinbox.value())
            #log.debug(f"Superfat set to: {self.calculator.superfat_percent}")
            # Pull Lye Type
            self.calculator.set_lye_type(settings.lye_combo.currentText())
            #log.debug(f"Lye type set to: {self.calculator.lye_type}")

            # Pull Water (This replaces the need for the loop-heavy sync_settings)
            method_text = settings.water_method_combo.currentText()
            val = settings.water_value_spinbox.value()

            mapping = {
                "Water:Lye Ratio": "ratio",
                "Water % of Oils": "percent",
                "Lye Concentration": "concentration"
            }
            method = mapping.get(method_text, "ratio")
            self.calculator.set_water_calc_method(method, val)
            #log.debug(f"Water calculation method set to: {self.calculator.water_calc_method}")


        except Exception as e:
            log.error(f"Failed to pull UI data into calculator: {e}")

        # --- STEP 1: CALCULATE (The 'Math') ---
        # Now when you call this, it uses the values we just pulled above!
        results = self.calculator.get_batch_properties()
        #log.debug("--- Starting Universal Calculation Update ---")

        # 1. Unit & Calculator Sync
        try:
            unit_pref = self.view._settings.value("unit_system", "grams").lower()
            self.calculator.unit_system = unit_pref
            #log.debug(f"Unit system synchronized to: {unit_pref}")
        except Exception as e:
            log.error(f"Failed to sync unit settings: {e}")

        # 2. Base Properties Retrieval
        try:
            results = self.calculator.get_batch_properties()
            results['unit_system_abbr'] = self.calculator.get_unit_abbreviation()
            #log.debug(f"Base batch properties retrieved: {list(results.keys())}")
        except Exception as e:
            #log.error(f"Calculator failed to provide batch properties: {e}")
            results = {} # Fallback to prevent crashes in later steps

        # 3. Masterbatch Logic
        try:
            settings_ui = self.view.recipe_tab.recipe_settings
            is_mb = settings_ui.masterbatch_check.isChecked()
            results['is_masterbatch'] = is_mb

            if is_mb:
                target_final = settings_ui.target_conc_spin.value()
                log.debug(f"Calculating Masterbatch: Lye={results.get('lye_weight')}g, Target={target_final}%")
                mb_math = self.calculator.calculate_masterbatch_pour(
                    target_lye_grams=results.get('lye_weight', 0),
                    mb_concentration=50.0,
                    final_target_conc=target_final
                )
                results.update(mb_math)
        except AttributeError as e:
            log.warning(f"Masterbatch UI elements missing or uninitialized: {e}")
        except Exception as e:
            log.error(f"Masterbatch math error: {e}")

        # 4. Costs & Yield (The 'Fragile' Section)
        total_cost = 0.0
        try:
            if self.cost_manager:
                # Check Oils
                for name, weight in self.calculator.oils.items():
                    cost = self.cost_manager.get_cost_per_gram(name)
                    if cost is None:
                        log.warning(f"Cost missing for Oil: '{name}'. Defaulting to 0.0")
                        cost = 0.0
                    total_cost += (weight * cost)

                # Check Additives
                for name, weight in self.calculator.additives.items():
                    cost = self.cost_manager.get_cost_per_gram(name)
                    if cost is None:
                        log.warning(f"Cost missing for Additive: '{name}'. Defaulting to 0.0")
                        cost = 0.0
                    total_cost += (weight * cost)

            results['total_batch_cost'] = total_cost
            #log.debug(f"Total ingredient cost calculated: {total_cost}")

            # Packaging & Yield
            res_widget = self.view.recipe_tab.results_widget
            results['packaging_cost'] = res_widget.ypacking_cost_spin.value()
            results['total_batch_cost'] += results['packaging_cost']

            total_weight = results.get('total_batch_weight', 0.0)
            bar_size = res_widget.bar_size_spin.value()
            results['yield'] = total_weight / bar_size if bar_size > 0 else 0.0

        except Exception as e:
            log.error(f"Cost/Yield calculation block failed: {e}")

        # 5. UI Updates
        try:
            self.view.recipe_tab.results_widget.update_display(results)

            # Name Sync
            recipe_name = getattr(self.view.current_recipe, 'name', "New Recipe")
            if hasattr(self.view.recipe_tab.results_widget, 'recipe_name_label'):
                self.view.recipe_tab.results_widget.recipe_name_label.setText(recipe_name)

            if hasattr(self.view, 'update_scale_label'):
                self.view.update_scale_label()
            #log.debug("UI labels and display widgets updated.")
        except Exception as e:
            log.error(f"UI display update failed: {e}")

        # 6. Table Refreshes (With Signal Safety)
        try:
            #log.debug("Refreshing UI tables...")
            self.view._suppress_oils_table_signals = True
            self.view._suppress_additives_table_signals = True

            self.view.update_oils_table()
            self.view.update_additives_table()

        except Exception as e:
            log.error(f"Table refresh failed: {e}")
        finally:
            # Crucial: Always re-enable signals even if refresh fails
            self.view._suppress_oils_table_signals = False
            self.view._suppress_additives_table_signals = False
            #log.debug("Table signals re-enabled.")

        #log.debug("--- Calculation Update Complete ---")

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

            #log.debug(f"Widget children: {dir(self.view.recipe_tab.recipe_settings)}")
            # Update UI controls to match loaded values
            self.view.recipe_tab.recipe_settings.superfat_spinbox.setValue(self.calculator.superfat_percent)
            self.view.recipe_tab.recipe_settings.lye_combo.setCurrentText(self.calculator.lye_type)
            method_to_text = {
                "ratio": "Water:Lye Ratio",
                "percent": "Water % of Oils",
                "concentration": "Lye Concentration"
            }
            self.view.recipe_tab.recipe_settings.water_method_combo.setCurrentText(method_to_text.get(self.calculator.water_calc_method, "Water:Lye Ratio"))

            #log.info(f"Successfully loaded and calculated: {loaded_recipe.name}")

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
    def perform_save(self):
        """Saves recipe by syncing all data to the object first."""
        name, ok = QInputDialog.getText(
            self.view, "Save Recipe", "Recipe Name:", text=self.view.current_recipe.name
        )

        if not (ok and name):
            return

        # 1. Sync EVERYTHING to the recipe object first
        r = self.view.current_recipe
        r.name = name
        r.oils = self.calculator.oils.copy()
        r.additives = self.calculator.additives.copy()
        r.lye_type = self.calculator.lye_type
        r.water_calc_method = self.calculator.water_calc_method
        r.water_to_lye_ratio = self.calculator.water_to_lye_ratio
        r.water_percent = self.calculator.water_percent
        r.lye_concentration = self.calculator.lye_concentration
        r.superfat_percent = self.calculator.superfat_percent

        # Add the notes to the object before saving
        # (Assuming your Recipe model has a .notes attribute)
        r.notes = self.view.recipe_tab.notes_widget.get_notes()

        # 2. Single Save Operation
        # The manager should handle the JSON conversion internally
        filepath = self.recipe_manager.save_recipe(r)

        if filepath:
            # Refresh the UI list
            self.view.manager_widget.refresh_recipe_list()
            log.info(f"Recipe saved successfully to {filepath}")

        self.update_calculations()
    #Load Recipe
    def on_load_clicked(self, filepath=None):
        """
        Handles loading. If filepath is provided (from Library), use it.
        If not (from Button), open the File Dialog.
        """
        #log.info("Load recipe initiated")
        # If no filepath was passed (meaning the 'Load' button was clicked)
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self.view, "Open Recipe", "recipes", "JSON Files (*.json)"
            )

        if filepath:
            # Pass the work to perform_load to keep this clean
            self.perform_load(filepath)