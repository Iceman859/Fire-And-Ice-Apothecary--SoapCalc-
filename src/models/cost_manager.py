"""
Manager for ingredient costs and COGS calculations.
"""

import json
import os
from typing import Dict, Any, Optional

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
                with open(self.filepath, 'r') as f:
                    self.costs = json.load(f)
            except Exception as e:
                print(f"Error loading costs: {e}")
                self.costs = {}
        else:
            self.costs = {}

    def save_costs(self):
        """Save costs to JSON file."""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.costs, f, indent=4)
        except Exception as e:
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
        self.costs[name] = {
            "price": price,
            "quantity": quantity,
            "unit": unit
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
        if unit in ["g", "grams", "gram"]: return amount
        if unit in ["oz", "ounces", "ounce"]: return amount * 28.3495
        if unit in ["lb", "lbs", "pounds", "pound"]: return amount * 453.592
        if unit in ["kg", "kilograms", "kilogram"]: return amount * 1000.0
            
        # Volume units (Approximation: 1g/ml)
        if unit in ["ml", "milliliters"]: return amount 
        if unit in ["l", "liters", "liter"]: return amount * 1000.0
        if unit in ["gal", "gallons", "gallon"]: return amount * 3785.41
        if unit in ["fl oz", "fluid ounces"]: return amount * 29.5735
            
        return amount