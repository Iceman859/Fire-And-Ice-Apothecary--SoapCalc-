"""
Manager for ingredient costs and COGS calculations.
"""

import json
import os
from typing import Any, Dict, Optional


class CostManager:
    """
    Manages ingredient costs for Cost of Goods Sold (COGS) calculations.

    Data is persisted to a JSON file to track user-specific pricing.
    """

    def __init__(self, filepath: str = "ingredient_costs.json"):
        self.filepath = filepath
        self.costs: Dict[str, Dict[str, Any]] = {}
        self.load_costs()

    def load_costs(self):
        """Load costs from JSON file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.costs = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading costs: {e}")
                self.costs = {}
        else:
            self.costs = {}

    def save_costs(self):
        """Save costs to JSON file."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.costs, f, indent=4)
        except (IOError, OSError) as e:
            print(f"Error saving costs: {e}")

    def set_cost(self, name: str, price: float, quantity: float, unit: str):
        """
        Set cost for an ingredient.

        Args:
            name: Ingredient name
            price: Total price paid (e.g., 15.99)
            quantity: Amount purchased (e.g., 16)
            unit: Unit of purchase ('g', 'oz', 'lbs', 'kg', 'l', 'gal')
        """
        self.costs[name] = {"price": price, "quantity": quantity, "unit": unit}
        self.save_costs()

    def add_stock(self, name: str, price: float, quantity: float, unit: str):
        """
        Add new stock to existing inventory using Weighted Average Cost.
        """
        if name not in self.costs:
            self.set_cost(name, price, quantity, unit)
            return

        # Get current state
        current_data = self.costs[name]
        current_unit = current_data.get("unit", "grams")
        current_qty = float(current_data.get("quantity", 0.0))
        current_total_value = float(current_data.get("price", 0.0))

        # Convert both to grams for calculation to ensure accuracy across units
        current_grams = self._convert_to_grams(current_qty, current_unit)
        added_grams = self._convert_to_grams(quantity, unit)

        new_grams = current_grams + added_grams
        new_total_value = current_total_value + price

        # Update (storing as grams to avoid unit confusion)
        self.costs[name] = {
            "price": round(new_total_value, 2),
            "quantity": round(new_grams, 2),
            "unit": "grams",
        }
        self.save_costs()

    def get_cost_data(self, name: str) -> Optional[Dict[str, Any]]:
        """Get raw cost data for an ingredient."""
        return self.costs.get(name)

    def get_cost_per_gram(self, name: str) -> float:
        """Calculate cost per gram for an ingredient."""
        data = self.costs.get(name)
        if not data:
            return 0.0

        price = float(data.get("price", 0.0))
        quantity = float(data.get("quantity", 1.0))
        unit = data.get("unit", "grams")

        if quantity <= 0:
            return 0.0

        # Convert quantity to grams
        grams = self._convert_to_grams(quantity, unit)
        if grams <= 0:
            return 0.0

        return price / grams

    def _convert_to_grams(self, amount: float, unit: str) -> float:
        """Convert various units to grams."""
        unit = unit.lower().strip()

        # Weight units
        if unit in ["g", "grams", "gram"]:
            return amount
        if unit in ["oz", "ounces", "ounce"]:
            return amount * 28.3495
        if unit in ["lb", "lbs", "pounds", "pound"]:
            return amount * 453.592
        if unit in ["kg", "kilograms", "kilogram"]:
            return amount * 1000.0

        # Volume units (Approximation: 1g/ml)
        if unit in ["ml", "milliliters"]:
            return amount
        if unit in ["l", "liters", "liter"]:
            return amount * 1000.0
        if unit in ["gal", "gallons", "gallon"]:
            return amount * 3785.41
        if unit in ["fl oz", "fluid ounces"]:
            return amount * 29.5735

        return amount

    def deduct_stock(self, name: str, amount_grams: float) -> float:
        """
        Deduct amount from inventory.
        Returns the remaining stock in grams, or -1 if item not found.
        """
        if name not in self.costs:
            return -1.0

        data = self.costs[name]
        current_qty = float(data.get("quantity", 0.0))
        unit = data.get("unit", "grams")

        # Convert deduction amount to inventory unit
        deduct_qty = self._convert_from_grams(amount_grams, unit)

        # Update quantity
        new_qty = max(0.0, current_qty - deduct_qty)
        data["quantity"] = round(new_qty, 2)
        self.save_costs()

        # Return remaining in grams for checking low stock
        return self._convert_to_grams(new_qty, unit)

    def _convert_from_grams(self, grams: float, unit: str) -> float:
        """Convert grams to target unit."""
        unit = unit.lower().strip()

        # Weight units
        if unit in ["g", "grams", "gram"]:
            return grams
        if unit in ["oz", "ounces", "ounce"]:
            return grams / 28.3495
        if unit in ["lb", "lbs", "pounds", "pound"]:
            return grams / 453.592
        if unit in ["kg", "kilograms", "kilogram"]:
            return grams / 1000.0

        # Volume units (Approximation: 1g = 1ml)
        if unit in ["ml", "milliliters"]:
            return grams
        if unit in ["l", "liters", "liter"]:
            return grams / 1000.0
        if unit in ["gal", "gallons", "gallon"]:
            return grams / 3785.41
        if unit in ["fl oz", "fluid ounces"]:
            return grams / 29.5735

        return grams

    def has_sufficient_stock(self, name: str, amount_grams: float) -> bool:
        """Check if there is enough stock for the given amount in grams."""
        # If we aren't tracking this item (not in DB), assume we have enough (don't block)
        if name not in self.costs:
            return True

        data = self.costs[name]
        current_qty = float(data.get("quantity", 0.0))
        unit = data.get("unit", "grams")

        required_qty = self._convert_from_grams(amount_grams, unit)
        return current_qty >= required_qty
