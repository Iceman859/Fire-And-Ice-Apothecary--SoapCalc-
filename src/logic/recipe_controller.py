import json
import os
from PyQt6.QtWidgets import QInputDialog, QFileDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from src import ui
from src.models.recipe import Recipe
from src.utils.logger import log
from src.utils.logger import log
from src.utils.html_helper import parse_artisan_html_recipe, extract_extended_notes

class RecipeController:
    def __init__(self, view, calculator, cost_manager, recipe_manager, batch_manager):
        """Restored full signature to match MainWindow initialization."""
        self.view = view
        self.calculator = calculator
        self.cost_manager = cost_manager
        self.recipe_manager = recipe_manager
        self.batch_manager = batch_manager

        if hasattr(self.view, 'recipe_tab'):
            self.setup_controller_connections()


    def setup_controller_connections(self):
            """Connects signals and context menus once the UI is built."""
            # 1. Right-click logic
            self.view.recipe_tab.additives_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.view.recipe_tab.additives_table.customContextMenuRequested.connect(self.show_additive_context_menu)

            # 2. Additive/Fragrance signals - CONNECT TO BOTH REFRESH AND MATH
            if hasattr(self.view.recipe_tab, 'fragrance_widget'):
                self.view.recipe_tab.fragrance_widget.fragrance_added.connect(self.refresh_additives_table)
                self.view.recipe_tab.fragrance_widget.fragrance_added.connect(self.update_calculations)

            if hasattr(self.view.recipe_tab, 'additive_widget'):
                self.view.recipe_tab.additive_widget.additive_added.connect(self.refresh_additives_table)
                self.view.recipe_tab.additive_widget.additive_added.connect(self.update_calculations)

    def show_oil_context_menu(self, position):
            """Triggered when right-clicking the oils table."""
            from PyQt6.QtWidgets import QMenu

            # Figure out which row was clicked
            index = self.view.oils_table.indexAt(position)
            if not index.isValid():
                return

            menu = QMenu()
            delete_action = menu.addAction("Remove Oil")

            # Show the menu at the cursor position
            action = menu.exec(self.view.oils_table.viewport().mapToGlobal(position))

            if action == delete_action:
                self.remove_oil_at_index(index.row())

    def remove_oil_at_index(self, row_index):
        """Tells the model to delete the oil and refreshes the math."""
        # 1. Tell the Model to perform the deletion
        # This ensures the Calculator's internal dictionary is updated
        self.view.recipe_model.removeRow(row_index)

        # 2. Recalculate everything now that an oil is gone
        self.update_calculations()

        # 3. Refresh additives in case their weights (based on % of oils) changed
        self.refresh_additives_table()

    def update_calculations(self):
            """Main calculation engine. Pulls from UI, runs math, pushes to UI."""
            try:
                # --- PRODUCT MODE CHECK ---
                is_body_product = False
                settings = self.view.recipe_tab.recipe_settings
                if hasattr(settings, 'product_mode_combo'):
                    is_body_product = settings.product_mode_combo.currentText() == "Body Scrubs/Butters"

                if hasattr(self.view.recipe_tab, 'recipe_model'):
                    self.view.recipe_tab.recipe_model.unit_system = self.calculator.unit_system

                    unit_system = self.calculator.unit_system

                    if hasattr(self.view, 'recipe_model'):
                        self.view.recipe_model.unit_system = unit_system

                # 1. Sync settings from UI to Calculator
                unit_system = self.calculator.unit_system

                # Only sync soap-specific math if NOT in body product mode
                if not is_body_product:
                    sf = settings.superfat_spinbox.value()
                    self.calculator.set_superfat(sf)

                    self.calculator.set_lye_type(settings.lye_combo.currentText())

                    method_map = {
                        "Water:Lye Ratio": "ratio",
                        "Water % of Oils": "percent",
                        "Lye Concentration": "concentration"
                    }
                    method_text = settings.water_method_combo.currentText()
                    method_key = method_map.get(method_text, "ratio")
                    method_val = settings.water_value_spinbox.value()
                    self.calculator.set_water_calc_method(method_key, method_val)

                # 2. Perform math in the Calculator
                results = self.calculator.get_batch_properties()
                results['unit_system_abbr'] = self.calculator.get_unit_abbreviation()

                # --- OVERWRITE FOR BODY PRODUCTS ---
                if is_body_product:
                    results['lye_weight'] = 0.0
                    results['water_weight'] = 0.0
                    # Total weight is just oils + additives
                    oil_total = sum(self.calculator.oils.values())
                    additive_total = sum(self.calculator.additives.values())
                    results['total_batch_weight'] = oil_total + additive_total

                # 3. Calculate Financials from current oils
                total_cost = 0.0
                for oil_name, weight_g in self.calculator.oils.items():
                    if self.cost_manager:
                        cost_per_g = self.cost_manager.get_cost_per_gram(oil_name)
                        if cost_per_g:
                            total_cost += cost_per_g * weight_g

                for additive_name, weight_g in self.calculator.additives.items():
                    if self.cost_manager:
                        cost_per_g = self.cost_manager.get_cost_per_gram(additive_name)
                        if cost_per_g:
                            total_cost += cost_per_g * weight_g

                results['total_batch_cost'] = total_cost

                # 4. Masterbatch Logic (if enabled and NOT a body product)
                is_mb = settings.masterbatch_check.isChecked() and not is_body_product
                results['is_masterbatch'] = is_mb

                if is_mb:
                    target_final = settings.target_conc_spin.value()
                    lye_grams = results.get('lye_weight', 0)
                    mb_math = self.calculator.calculate_masterbatch_pour(
                        target_lye_grams=lye_grams,
                        mb_concentration=50.0,
                        final_target_conc=target_final
                    )
                    results.update(mb_math)

                # 5. Yield & Unit Cost Calculation
                results_widget = self.view.results_widget
                bar_size = results_widget.bar_size_spin.value()
                pkg_cost = results_widget.pkg_cost_spin.value()
                total_batch_weight = results.get('total_batch_weight', 0.0)

                if bar_size > 0:
                    results['est_yield'] = total_batch_weight / bar_size
                    if results['est_yield'] > 0:
                        results['total_batch_cost'] += (pkg_cost * results['est_yield'])
                        results['cost_per_unit'] = results['total_batch_cost'] / results['est_yield']
                    else:
                        results['cost_per_unit'] = 0.0
                else:
                    results['est_yield'] = 0.0
                    results['cost_per_unit'] = 0.0

                # 6. Push to Results Widget
                results['is_body_product'] = is_body_product
                results_widget.update_display(results)

                # 7. Update Tables (with model refresh)
                self.view._suppress_oils_table_signals = True
                self.view._suppress_additives_table_signals = True

                try:
                    if hasattr(self.view.recipe_tab, 'recipe_model'):
                        self.view.recipe_tab.recipe_model.layoutChanged.emit()

                    if hasattr(self.view, 'update_additives_table'):
                        self.view.update_additives_table()
                except Exception as e:
                    log.error(f"Table refresh failed: {e}")
                finally:
                    self.view._suppress_oils_table_signals = False
                    self.view._suppress_additives_table_signals = False

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

    def remove_selected_additive(self):
            """Removes the highlighted additive row and updates math."""
            table = self.view.recipe_tab.additives_table
            selected = table.selectedItems()
            if not selected:
                return

            # Get the name from the first column of the selected row
            row = selected[0].row()
            name = table.item(row, 0).text()

            if name in self.calculator.additives:
                del self.calculator.additives[name]
                self.refresh_additives_table()
                self.update_calculations()
                self.view.statusBar().showMessage(f"Removed {name}")

    def on_new_clicked(self):
        """Resets the state for a brand new recipe with clean UI defaults."""
        # 1. Clear the Brain (Calculator)
        self.calculator.oils.clear()
        self.calculator.additives.clear()

        # 2. Reset the Metadata
        self.view.current_recipe = Recipe()
        self.view.current_recipe.name = "New Recipe"
        self.view.recipe_tab.recipe_name_label.setText("New Recipe")
        self.view.recipe_tab.notes_widget.set_notes("")

        # 3. RESET THE UI SETTINGS (Crucial for robustness)
        ui = self.view.recipe_settings
        ui.superfat_spinbox.setValue(5.0)  # Standard default
        ui.lye_combo.setCurrentText("NaOH")
        ui.water_method_combo.setCurrentText("Water:Lye Ratio")
        ui.water_value_spinbox.setValue(2.0)

        # Clear Luxury Formulation inputs
        ui.scent_top_name.clear()
        ui.scent_top_desc.clear()
        ui.scent_mid_name.clear()
        ui.scent_mid_desc.clear()
        ui.scent_base_name.clear()
        ui.scent_base_desc.clear()
        if hasattr(ui, 'instructions_input'):
            ui.instructions_input.clear()

        # 4. Handle Units and Batch Weight
        unit_pref = self.view._settings.value("unit_system", "grams").lower()
        conv = 28.3495231

        if unit_pref == "ounces":
            self.calculator.total_batch_weight = 32.0 * conv
            if hasattr(ui, 'unit_toggle'):
                ui.unit_toggle.setCurrentText("Ounces")
        elif unit_pref == "pounds":
            self.calculator.total_batch_weight = 2.0 * 16 * conv
            if hasattr(ui, 'unit_toggle'):
                ui.unit_toggle.setCurrentText("Pounds")
        else:
            self.calculator.total_batch_weight = 1000.0
            if hasattr(ui, 'unit_toggle'):
                ui.unit_toggle.setCurrentText("Grams")

        # 5. Refresh Table and Run Math
        if hasattr(self.view.recipe_tab, 'recipe_model'):
            self.view.recipe_tab.recipe_model.refresh()

        self.view.recipe_tab.additives_table.setRowCount(0)
        self.update_calculations()

        self.view.statusBar().showMessage("New recipe created and UI reset.")

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
        """Logic for saving the recipe including new Luxury Formulation data."""
        current_name = self.view.current_recipe.name or ""
        name, ok = QInputDialog.getText(self.view, "Save", "Recipe Name:", text=current_name)

        if ok and name:
            recipe = self.view.current_recipe
            ui = self.view.recipe_settings

        # --- Standard Data ---
            recipe.name = name
            recipe.oils = self.calculator.oils.copy()
            recipe.additives = self.calculator.additives.copy()
            recipe.notes = self.view.recipe_tab.notes_widget.get_notes()

            # --- Syncing your UI specifically ---
            recipe.lye_type = ui.lye_combo.currentText()
            recipe.superfat_percent = ui.superfat_spinbox.value()

            # Save the METHOD (Ratio, %, or Concentration)
            recipe.water_calc_method = ui.water_method_combo.currentText()

            # Save the VALUE (This is the 2.0 or 33.0 or 38.0 from that shared box)
            # In your code, this is always 'water_value_spinbox'
            recipe.water_percent = ui.water_value_spinbox.value()

            # If you use the 50/50 masterbatch toggle
            recipe.use_masterbatch = ui.masterbatch_check.isChecked()

            # --- Scent Profile ---
            recipe.scent_top = {
                "name": ui.scent_top_name.text(),
                "description": ui.scent_top_desc.text()
            }
            recipe.scent_mid = {
                "name": ui.scent_mid_name.text(),
                "description": ui.scent_mid_desc.text()
            }
            recipe.scent_base = {
                "name": ui.scent_base_name.text(),
                "description": ui.scent_base_desc.text()
            }

            # --- Manufacturing Instructions ---
            recipe.instructions = self.view.recipe_settings.get_instructions()

            log.debug(f"Saving File with these parameters: Name={recipe.name}, Oils={recipe.oils}, Additives={recipe.additives}, Superfat={recipe.superfat_percent}, Lye Type={recipe.lye_type}, Water Method={recipe.water_calc_method}, Water Value={recipe.water_percent}, Masterbatch={recipe.use_masterbatch}")

            # --- Execute Save ---
            path = self.recipe_manager.save_recipe(recipe)
            if path:
                self.view.statusBar().showMessage(f"Successfully saved {name}")
                self.view.manager_widget.refresh_recipe_list()

    def perform_load(self, filepath):
        """Robust load logic that syncs the file data to the UI before calculating."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Convert JSON dict to your Recipe object
            loaded = Recipe.from_dict(data)
            ui = self.view.recipe_settings

            # Block signals to prevent unwanted math during UI sync
            ui.water_method_combo.blockSignals(True)
            ui.water_value_spinbox.blockSignals(True)
            ui.superfat_spinbox.blockSignals(True)

            # 1. SYNC UI SETTINGS (Do this before the math runs)
            # -------------------------------------------------
            # Force Unit System (Oz vs Grams)
            if hasattr(ui, 'unit_toggle'):
                # Assuming your unit_toggle is a QComboBox or similar
                ui.unit_toggle.setCurrentText(loaded.unit_system)

            # Set Superfat and Lye Type
            ui.superfat_spinbox.setValue(loaded.superfat_percent)
            ui.lye_combo.setCurrentText(loaded.lye_type)

            # Set the Water Method (Dropdown) FIRST
            ui.water_method_combo.setCurrentText(loaded.water_calc_method)

            # Set the Water Value (The 2.0, 33.0, etc.) SECOND
            # This ensures the spinbox is interpreted correctly by the UI
            ui.water_value_spinbox.setValue(loaded.water_percent)
            self.view.recipe_settings.on_water_method_changed(loaded.water_calc_method)

            #Unlock signals after syncing
            ui.water_method_combo.blockSignals(False)
            ui.water_value_spinbox.blockSignals(False)
            ui.superfat_spinbox.blockSignals(False)



            # Scent Profile (Luxury Formulation)
            ui.scent_top_name.setText(loaded.scent_top.get("name", ""))
            ui.scent_top_desc.setText(loaded.scent_top.get("description", ""))
            ui.scent_mid_name.setText(loaded.scent_mid.get("name", ""))
            ui.scent_mid_desc.setText(loaded.scent_mid.get("description", ""))
            ui.scent_base_name.setText(loaded.scent_base.get("name", ""))
            ui.scent_base_desc.setText(loaded.scent_base.get("description", ""))

            # Instructions
            if hasattr(ui, 'instructions_input'):
                ui.instructions_input.setPlainText(loaded.instructions)

            # 2. UPDATE UNDERLYING DATA
            # -------------------------------------------------
            self.view.recipe_tab.recipe_name_label.setText(loaded.name)
            self.calculator.oils = loaded.oils.copy()
            self.calculator.additives = data.get("additives", {}).copy()

            # Update the Recipe object reference in the view
            self.view.current_recipe = loaded

            # 3. REFRESH & CALCULATE
            # -------------------------------------------------
            # Refresh the table model to show the new oils
            if hasattr(self.view.recipe_tab, 'recipe_model'):
                self.view.recipe_tab.recipe_model.refresh()

            self.refresh_additives_table()

            # FINALLY: Run calculations once the UI reflects all loaded values
            self.update_calculations()

            self.view.statusBar().showMessage(f"Successfully loaded: {loaded.name}")

        except Exception as e:
            # log.error is good, but show a message to yourself in the UI too
            self.view.statusBar().showMessage(f"Load Error: {str(e)}")
            print(f"Detailed Error: {e}")

    def on_load_clicked(self, filepath=None):
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(self.view, "Load Recipe", "recipes", "JSON (*.json)")
        if filepath:
            self.perform_load(filepath)

    def on_import_clicked(self):
        parent_widget = self.view if hasattr(self, 'view') else None
        file_name, _ = QFileDialog.getOpenFileName(parent_widget, "Open Recipe HTML", "", "HTML Files (*.html)")

        if not file_name:
            return

        # 1. Parse the file once
        data = parse_artisan_html_recipe(file_name)

        if data:
            # 2. Set the Title/Name
            recipe_name = data.get('title', "Unknown Recipe")
            self.view.current_recipe.name = recipe_name

            if hasattr(self.view.recipe_tab, 'recipe_name_input'):
                self.view.recipe_tab.recipe_name_input.setText(recipe_name)

            # 3. Import Ingredients (The Oils/Fats)
            # We clear the existing list first if your UI supports it,
            # then loop through every phase found in the HTML.
            for phase_name, ingredients in data.get("phases", {}).items():
                for ing in ingredients:
                    # Pointing to oil_input_widget as per your previous snippet
                    if hasattr(self.view, 'oil_input_widget'):
                        self.view.oil_input_widget.add_oil_from_import(ing["name"], ing["weight"])

            # 4. Refresh the Table Model
            if hasattr(self.view.recipe_tab, 'recipe_model'):
                self.view.recipe_tab.recipe_model.beginResetModel()
                self.view.recipe_tab.recipe_model.endResetModel()

            # 5. Update Math
            self.update_calculations()

            # 6. DISTRIBUTE LUXURY DATA TO recipe_settings
            try:
                ext = data.get("extended_data", {})
                # Updated to your actual variable name: recipe_settings
                ui = self.view.recipe_settings

                # Set Instructions
                if hasattr(ui, 'instructions_input'):
                    ui.instructions_input.setPlainText(ext.get("instructions", ""))

                # Set Scent Profile (Top, Mid, Base)
                # We pull from the nested dicts we created in extract_extended_notes
                scents = {
                    "top": (ui.scent_top_name, ui.scent_top_desc, ext.get("scent_top", {})),
                    "mid": (ui.scent_mid_name, ui.scent_mid_desc, ext.get("scent_mid", {})),
                    "base": (ui.scent_base_name, ui.scent_base_desc, ext.get("scent_base", {}))
                }

                for prefix, (name_field, desc_field, val_dict) in scents.items():
                    if name_field and desc_field:
                        name_field.setText(str(val_dict.get("name", "")))
                        desc_field.setText(str(val_dict.get("description", "")))

                # Set the Artisan's Note
                if hasattr(self.view.recipe_tab, 'notes_widget'):
                    note_text = ext.get("notes", "")
                    # Direct check to see if notes_widget is a QTextEdit or custom
                    if hasattr(self.view.recipe_tab.notes_widget, 'setPlainText'):
                        self.view.recipe_tab.notes_widget.setPlainText(note_text)
                    else:
                        self.view.recipe_tab.notes_widget.set_notes(note_text)

            except Exception as e:
                print(f"Error distributing extended data to recipe_settings: {e}")

    def show_additive_context_menu(self, position):
            from PyQt6.QtWidgets import QMenu
            menu = QMenu()
            delete_action = menu.addAction("Delete Additive")
            action = menu.exec(self.view.recipe_tab.additives_table.mapToGlobal(position))
            if action == delete_action:
                self.remove_selected_additive()