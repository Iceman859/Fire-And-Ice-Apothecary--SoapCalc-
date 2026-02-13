"""
Calculator model for Gummy formulations.
"""

from typing import Dict
from ..data.gummy_ingredients import GUMMY_INGREDIENTS

class GummyCalculator:
    def __init__(self):
        self.ingredients: Dict[str, float] = {} # name: weight
        self.total_weight = 0.0
        self.target_brix = 78.0 # Standard finishing brix for shelf-stable gummies

    def add_ingredient(self, name: str, weight: float):
        """Add or update an ingredient in the recipe."""
        if weight > 0:
            self.ingredients[name] = weight
        elif name in self.ingredients:
            del self.ingredients[name]
        self._calculate_totals()

    def remove_ingredient(self, name: str):
        """Remove an ingredient from the recipe."""
        if name in self.ingredients:
            del self.ingredients[name]
        self._calculate_totals()

    def _calculate_totals(self):
        self.total_weight = sum(self.ingredients.values())

    def calculate_total_solids(self) -> float:
        """Calculate total soluble solids weight in the batch."""
        total_solids = 0.0
        for name, weight in self.ingredients.items():
            data = GUMMY_INGREDIENTS.get(name, {})
            solids_pct = data.get("solids", 0.0)
            total_solids += weight * (solids_pct / 100.0)
        return total_solids

    def calculate_estimated_yield(self) -> float:
        """Calculate estimated final batch weight based on target Brix."""
        total_solids = self.calculate_total_solids()
        if self.target_brix <= 0:
            return 0.0
        # Final Weight = Total Solids / Target Brix (e.g. 0.78)
        return total_solids / (self.target_brix / 100.0)

    def calculate_water_to_remove(self) -> float:
        """
        Calculate amount of water that needs to be boiled off to reach target Brix.
        
        Water to Remove = Current Total Weight - Estimated Final Yield
        """
        current_weight = self.total_weight
        target_weight = self.calculate_estimated_yield()
        return max(0.0, current_weight - target_weight)

    def calculate_mold_requirements(self, count: int, volume_per_cavity: float, density: float = 1.35) -> float:
        """
        Calculate required batch weight for a specific number of molds.
        
        Args:
            count: Number of cavities/molds
            volume_per_cavity: Volume in ml per cavity
            density: Density in g/ml (default 1.35 for gummies)
        """
        total_volume = count * volume_per_cavity
        return total_volume * density

    def scale_recipe(self, new_total_weight: float):
        """Scale all ingredients to match a new total weight."""
        if self.total_weight <= 0:
            return
        
        factor = new_total_weight / self.total_weight
        for name in self.ingredients:
            self.ingredients[name] *= factor
        
        self._calculate_totals()

    def get_doctoring_ratio(self) -> str:
        """
        Calculate the ratio of Sugar (Sucrose) to Corn Syrup (Glucose).
        Target is typically 1.2:1 to 1.5:1.
        """
        sugar = self.ingredients.get("Sugar (Sucrose)", 0.0)
        syrup = self.ingredients.get("Corn Syrup (43 DE)", 0.0)
        
        if syrup <= 0:
            return "No Syrup" if sugar > 0 else "N/A"
        
        ratio = sugar / syrup
        return f"{ratio:.2f}:1"

    def get_recipe_dict(self) -> Dict:
        """Get recipe data as dictionary."""
        return {
            "ingredients": self.ingredients.copy(),
            "target_brix": self.target_brix
        }

    def load_recipe_dict(self, data: Dict):
        """Load recipe data from dictionary."""
        self.ingredients = data.get("ingredients", {}).copy()
        self.target_brix = data.get("target_brix", 78.0)
        self._calculate_totals()