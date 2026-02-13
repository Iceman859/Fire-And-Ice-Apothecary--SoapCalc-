"""
Recipe model and manager for Gummy formulations.
"""

import json
import os
from typing import Dict, Optional

class GummyRecipe:
    def __init__(self, name: str = ""):
        self.name = name
        self.ingredients: Dict[str, float] = {}
        self.target_brix: float = 78.0
        self.notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "ingredients": self.ingredients,
            "target_brix": self.target_brix,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict):
        recipe = cls(data.get("name", ""))
        recipe.ingredients = data.get("ingredients", {})
        recipe.target_brix = data.get("target_brix", 78.0)
        recipe.notes = data.get("notes", "")
        return recipe


class GummyRecipeManager:
    def __init__(self, directory: str = "gummy_recipes"):
        self.directory = directory
        if not os.path.exists(directory):
            os.makedirs(directory)

    def save_recipe(self, recipe: GummyRecipe) -> str:
        """Save recipe to JSON file. Returns filepath."""
        safe_name = "".join(c for c in recipe.name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_name:
            safe_name = "untitled"
        filename = f"{safe_name}.json"
        filepath = os.path.join(self.directory, filename)
        
        with open(filepath, 'w') as f:
            json.dump(recipe.to_dict(), f, indent=4)
        return filepath

    def load_recipe(self, filepath: str) -> Optional[GummyRecipe]:
        """Load recipe from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return GummyRecipe.from_dict(data)