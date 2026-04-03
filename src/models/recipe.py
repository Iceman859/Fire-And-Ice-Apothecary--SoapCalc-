"""Recipe data model and management"""
# imports
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Recipe class represents a soap recipe with all its properties and methods
# to convert to/from dictionary for JSON serialization.
class Recipe:
    """Represents a soap recipe"""
    # init
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
        self.instructions = ""
        self.batch_weight = 0.0
        self.water_calc_method = "ratio"
        self.water_percent = 38.0
        self.lye_concentration = 33.40

        # NEW: Scent Profile Data
        self.scent_top = {"name": "", "description": ""}
        self.scent_mid = {"name": "", "description": ""}
        self.scent_base = {"name": "", "description": ""}

    # to_dict and from_dict methods for JSON serialization
    def to_dict(self) -> dict:
        """Convert recipe to dictionary"""
        return {
            "name": self.name,
            "unit_system": self.unit_system,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "oils": self.oils.copy(),
            "additives": self.additives.copy(), # FIXED: Added to dict
            "superfat_percent": self.superfat_percent,
            "water_to_lye_ratio": self.water_to_lye_ratio,
            "lye_type": self.lye_type,
            "notes": self.notes,
            "instructions": self.instructions, # NEW
            "batch_weight": self.batch_weight,
            "water_calc_method": self.water_calc_method,
            "water_percent": self.water_percent,
            "lye_concentration": self.lye_concentration,
            # NEW: Scent Profile
            "scent_top": self.scent_top.copy(),
            "scent_mid": self.scent_mid.copy(),
            "scent_base": self.scent_base.copy(),
        }

    # from_dict class method to create a Recipe instance from a dictionary
    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        """Create recipe from dictionary"""
        recipe = cls(data.get("name", "Untitled Recipe"))
        recipe.created_date = data.get("created_date", recipe.created_date)
        recipe.modified_date = data.get("modified_date", recipe.modified_date)
        recipe.oils = data.get("oils", {}).copy()
        recipe.additives = data.get("additives", {}).copy() # FIXED: Added to load
        recipe.superfat_percent = data.get("superfat_percent", 5.0)
        recipe.water_to_lye_ratio = data.get("water_to_lye_ratio", 2.0)
        recipe.lye_type = data.get("lye_type", "NaOH")
        recipe.notes = data.get("notes", "")
        recipe.instructions = data.get("instructions", "") # NEW
        recipe.batch_weight = data.get("batch_weight", 0.0)
        recipe.water_calc_method = data.get("water_calc_method", "ratio")
        recipe.water_percent = data.get("water_percent", 38.0)
        recipe.lye_concentration = data.get("lye_concentration", 30.0)

        # NEW: Scent Profile loading with defaults to prevent crashes on old files
        recipe.scent_top = data.get("scent_top", {"name": "", "description": ""})
        recipe.scent_mid = data.get("scent_mid", {"name": "", "description": ""})
        recipe.scent_base = data.get("scent_base", {"name": "", "description": ""})

        return recipe

# RecipeManager handles all file operations related to recipes
class RecipeManager:
    """Manages saving and loading recipes"""
    # init with default recipes directory
    def __init__(self, recipes_dir: str = "recipes"):
        self.recipes_dir = Path(recipes_dir)
        self.recipes_dir.mkdir(exist_ok=True)

    # save_recipe method saves a Recipe object to a JSON file.
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
            # If it's already a dict, dump it directly.
            # If it's an object, call to_dict() first.
            if isinstance(recipe, dict):
                json.dump(recipe, f, indent=2)
            else:
                json.dump(recipe.to_dict(), f, indent=2)

        return str(filepath)

    # load_recipe method loads a Recipe object from a JSON file.
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

    # list_recipes method lists all saved recipes in the recipes directory.
    def list_recipes(self) -> list:
        """List all saved recipes"""
        recipes = []
        for filepath in self.recipes_dir.glob("*.json"):
            recipe = self.load_recipe(filepath)
            if recipe:
                recipes.append((filepath.stem, recipe.name, filepath))
        return sorted(recipes, key=lambda x: x[1])

    # delete_recipe method deletes a recipe file specified by the filepath.
    def delete_recipe(self, filepath: str) -> bool:
        """Delete a recipe file"""
        try:
            Path(filepath).unlink()
            return True
        except FileNotFoundError:
            return False