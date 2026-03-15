from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import pyqtSignal

class RecipeManagementWidget(QWidget):
    """Widget for managing saved recipes"""

    # This is the only way this widget should talk to the rest of the app
    recipe_selected_signal = pyqtSignal(str)
    recipe_deleted_signal = pyqtSignal()

    def __init__(self, recipe_manager):
        super().__init__()
        self.recipe_manager = recipe_manager
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Saved Recipes:"))

        self.recipes_table = QTableWidget()
        self.recipes_table.setColumnCount(2)
        self.recipes_table.setHorizontalHeaderLabels(["Recipe Name", "File Path"])
        self.recipes_table.setColumnWidth(0, 200)
        self.recipes_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.recipes_table)

        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_recipe_list)

        load_btn = QPushButton("Load Selected")
        load_btn.clicked.connect(self.emit_load_signal) # Changed logic here

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)

        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(load_btn)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.refresh_recipe_list()

    def refresh_recipe_list(self):
        """Asks the manager for files and fills the table"""
        recipes = self.recipe_manager.list_recipes()
        self.recipes_table.setRowCount(len(recipes))
        for row, (filename, name, filepath) in enumerate(recipes):
            self.recipes_table.setItem(row, 0, QTableWidgetItem(name))
            self.recipes_table.setItem(row, 1, QTableWidgetItem(str(filepath)))

    def emit_load_signal(self):
        """Just tells the world which path was picked"""
        row = self.recipes_table.currentRow()
        if row >= 0:
            filepath = self.recipes_table.item(row, 1).text()
            self.recipe_selected_signal.emit(filepath)

    def delete_selected(self):
        """Delete logic stays here, but notifies the app to refresh if needed"""
        row = self.recipes_table.currentRow()
        if row >= 0:
            filepath = self.recipes_table.item(row, 1).text()
            if self.recipe_manager.delete_recipe(filepath):
                self.refresh_recipe_list()
                self.recipe_deleted_signal.emit()