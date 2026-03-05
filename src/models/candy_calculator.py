"""Calculation model for candy making"""

from typing import Dict


class CandyCalculator:
    """Main calculator for candy recipe calculations"""

    def __init__(self):
        self.ingredients = {}  # {ingredient_name: weight_in_grams}
        self.unit_system = "grams"  # "grams", "ounces", "pounds"

    def add_ingredient(self, name: str, weight: float):
        """Add or update an ingredient in the recipe"""
        if weight > 0:
            self.ingredients[name] = weight
        elif name in self.ingredients:
            del self.ingredients[name]

    def remove_ingredient(self, name: str):
        """Remove ingredient from the recipe"""
        if name in self.ingredients:
            del self.ingredients[name]

    def get_total_weight(self) -> float:
        """Get total weight of all ingredients"""
        return sum(self.ingredients.values())

    def get_batch_properties(self) -> Dict[str, float]:
        """
        Calculate batch properties. For candy, this is simpler.
        """
        total_weight = self.get_total_weight()

        # The UI expects these keys, so we provide dummy/mapped values
        return {
            "total_ingredient_weight": round(total_weight, 2),
            "total_batch_weight": round(
                total_weight, 2
            ),  # In candy, ingredients are the whole batch
            "total_oil_weight": round(total_weight, 2),  # Map this for the UI scale box
            "lye_weight": 0.0,
            "water_weight": self.ingredients.get("Water", 0.0),
            "relative_qualities": {},
            "fa_breakdown": {},
        }

    def scale_recipe(self, new_total_weight: float):
        """
        Scale the entire recipe to a new total weight.
        """
        current_total = self.get_total_weight()
        if current_total == 0:
            return

        scale_factor = new_total_weight / current_total
        for name in self.ingredients:
            self.ingredients[name] = round(self.ingredients[name] * scale_factor, 2)

    def set_unit_system(self, unit: str):
        """Set unit system ('grams', 'ounces', 'pounds')"""
        if unit in ["grams", "ounces", "pounds"]:
            self.unit_system = unit

    def convert_weight(self, weight_grams: float, to_unit: str) -> float:
        if to_unit == "grams":
            return weight_grams
        elif to_unit == "ounces":
            return weight_grams / 28.3495
        elif to_unit == "pounds":
            return weight_grams / 453.592
        return weight_grams

    def convert_to_grams(self, weight: float, from_unit: str) -> float:
        if from_unit == "grams":
            return weight
        elif from_unit == "ounces":
            return weight * 28.3495
        elif from_unit == "pounds":
            return weight * 453.592
        return weight

    def get_unit_abbreviation(self) -> str:
        """Get abbreviation for current unit system"""
        abbr = {"grams": "g", "ounces": "oz", "pounds": "lbs"}
        return abbr.get(self.unit_system, "g")

    # --- Compatibility properties to work with the existing UI ---
    def get_total_oil_weight(self):
        return self.get_total_weight()

    def add_oil(self, name, weight):
        self.add_ingredient(name, weight)

    @property
    def oils(self):
        return self.ingredients

    @property
    def additives(self):
        return self.ingredients

    # --- Compatibility methods for UI ---
    def set_superfat(self, percent: float):
        """Dummy method for UI compatibility."""
        pass

    def set_lye_type(self, lye_type: str):
        """Dummy method for UI compatibility."""
        pass

    def set_water_calc_method(self, method: str, value: float = None):
        """Dummy method for UI compatibility."""
        pass
