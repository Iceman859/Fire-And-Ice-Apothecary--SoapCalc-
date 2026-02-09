"""Recipe data model and management"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class Recipe:
    """Represents a soap recipe"""
    
    def __init__(self, name: str = "Untitled Recipe"):
        self.name = name
        self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
        self.oils = {}  # {oil_name: weight}
        self.superfat_percent = 5.0
        self.water_to_lye_ratio = 2.0
        self.lye_type = "NaOH"
        self.notes = ""
        self.batch_weight = 0.0
    
    def to_dict(self) -> dict:
        """Convert recipe to dictionary"""
        return {
            "name": self.name,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "oils": self.oils.copy(),
            "superfat_percent": self.superfat_percent,
            "water_to_lye_ratio": self.water_to_lye_ratio,
            "lye_type": self.lye_type,
            "notes": self.notes,
            "batch_weight": self.batch_weight,
        }
    
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
        return recipe


class RecipeManager:
    """Manages saving and loading recipes"""
    
    def __init__(self, recipes_dir: str = "recipes"):
        self.recipes_dir = Path(recipes_dir)
        self.recipes_dir.mkdir(exist_ok=True)
    
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
        
        with open(filepath, "w") as f:
            json.dump(recipe.to_dict(), f, indent=2)
        
        return str(filepath)
    
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
    
    def list_recipes(self) -> list:
        """List all saved recipes"""
        recipes = []
        for filepath in self.recipes_dir.glob("*.json"):
            recipe = self.load_recipe(filepath)
            if recipe:
                recipes.append((filepath.stem, recipe.name, filepath))
        return sorted(recipes, key=lambda x: x[1])
    
    def delete_recipe(self, filepath: str) -> bool:
        """Delete a recipe file"""
        try:
            Path(filepath).unlink()
            return True
        except FileNotFoundError:
            return False
