"""Recipe data model and management"""
    #imports
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
    #Recipe class represents a soap recipe with all its properties and methods to convert to/from dictionary for JSON serialization. RecipeManager handles saving, loading, listing, and deleting recipe files in a specified directory.
class Recipe:
    """Represents a soap recipe"""
    #init
    def __init__(self, name: str = "Untitled Recipe"):
        self.name = name
        self.unit_system = "Grams"
        self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
        self.oils = {}  # {oil_name: weight}
        self.additives = {}  # {additive_name: weight}
        self.superfat_percent = 5.0
        self.water_to_lye_ratio = 2.0
        self.lye_type = "NaOH"
        self.notes = ""
        self.batch_weight = 0.0
        self.water_calc_method = "ratio"
        self.water_percent = 38.0
        self.lye_concentration = 33.40
    #to_dict and from_dict methods for JSON serialization
    def to_dict(self) -> dict:
        """Convert recipe to dictionary"""
        return {
            "name": self.name,
            "unit_system": self.unit_system,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "oils": self.oils.copy(),
            "superfat_percent": self.superfat_percent,
            "water_to_lye_ratio": self.water_to_lye_ratio,
            "lye_type": self.lye_type,
            "notes": self.notes,
            "batch_weight": self.batch_weight,
            "water_calc_method": self.water_calc_method,
            "water_percent": self.water_percent,
            "lye_concentration": self.lye_concentration,
        }
    #from_dict class method to create a Recipe instance from a dictionary, providing default values for any missing keys.
    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """Create recipe from dictionary"""
        recipe = cls(data.get("name", "Untitled Recipe"))
        recipe.created_date = data.get("created_date", recipe.created_date)
        recipe.modified_date = data.get("modified_date", recipe.modified_date)
        recipe.oils = data.get("oils", {}).copy()
        recipe.superfat_percent = data.get("superfat_percent", 5.0)
        recipe.water_to_lye_ratio = data.get("water_to_lye_ratio", 2.0)
        recipe.lye_type = data.get("lye_type", "NaOH")
        recipe.notes = data.get("notes", "")
        recipe.batch_weight = data.get("batch_weight", 0.0)
        recipe.water_calc_method = data.get("water_calc_method", "ratio")
        recipe.water_percent = data.get("water_percent", 38.0)
        recipe.lye_concentration = data.get("lye_concentration", 30.0)
        return recipe

#RecipeManager handles all file operations related to recipes, including saving a recipe to a JSON file, loading a recipe from a JSON file, listing all saved recipes, and deleting a recipe file. It ensures that the recipes are stored in a specified directory and provides methods for managing the recipe files effectively.
class RecipeManager:
    """Manages saving and loading recipes"""
    #init with default recipes directory
    def __init__(self, recipes_dir: str = "recipes"):
        self.recipes_dir = Path(recipes_dir)
        self.recipes_dir.mkdir(exist_ok=True)
    #save_recipe method saves a Recipe object to a JSON file. It generates a filename based on the recipe name (or uses a provided custom filename), ensures the filename is valid, and writes the recipe data to the specified file in JSON format.
    def save_recipe(self, recipe: Recipe, filename: Optional[str] = None) -> str:
        """
        Save a recipe to JSON file.

        Args:
            recipe: Recipe object to save
            filename: Optional custom filename (without extension)

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = recipe.name.replace(" ", "_").lower()

        # Ensure valid filename
        filename = "".join(c for c in filename if c.isalnum() or c in ("-", "_"))
        filepath = self.recipes_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
                    # CHECK: If it's already a dict, dump it directly.
                    # If it's an object, call to_dict() first.
                    if isinstance(recipe, dict):
                        json.dump(recipe, f, indent=2)
                    else:
                        json.dump(recipe.to_dict(), f, indent=2)

        return str(filepath)

    #load_recipe method loads a Recipe object from a JSON file. It checks if the specified file exists, reads the JSON data, and converts it back into a Recipe object using the from_dict method. If the file is not found or if there is an error in decoding the JSON, it returns None.
    def load_recipe(self, filepath: str) -> Optional[Recipe]:
        """
        Load a recipe from JSON file.

        Args:
            filepath: Path to recipe file

        Returns:
            Recipe object or None if file not found
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return None

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return Recipe.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None
    #list_recipes method lists all saved recipes in the recipes directory. It iterates through all JSON files in the directory, loads each recipe, and collects their names and file paths into a list. The list is then sorted alphabetically by recipe name before being returned.
    def list_recipes(self) -> list:
        """List all saved recipes"""
        recipes = []
        for filepath in self.recipes_dir.glob("*.json"):
            recipe = self.load_recipe(filepath)
            if recipe:
                recipes.append((filepath.stem, recipe.name, filepath))
        return sorted(recipes, key=lambda x: x[1])
    #delete_recipe method deletes a recipe file specified by the filepath. It attempts to unlink (delete) the file and returns True if successful. If the file is not found, it catches the FileNotFoundError and returns False, indicating that the deletion was unsuccessful.
    def delete_recipe(self, filepath: str) -> bool:
        """Delete a recipe file"""
        try:
            Path(filepath).unlink()
            return True
        except FileNotFoundError:
            return False
