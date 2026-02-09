"""Calculation models for soap making"""

from typing import Dict, List, Tuple
from ..data.oils import get_oil_sap


class SoapCalculator:
    """Main calculator for soap recipe calculations"""
    
    def __init__(self):
        self.oils = {}  # {oil_name: weight_in_grams}
        self.superfat_percent = 5.0  # Default 5% superfat
        self.water_to_lye_ratio = 2.0  # Default 2:1 water to lye
        self.lye_type = "NaOH"  # NaOH, KOH, or 90% KOH
        self.total_batch_weight = 0.0
        self.unit_system = "grams"  # "grams", "ounces", "pounds"
        self.water_calc_method = "ratio"  # "ratio", "percent", "concentration"
        self.water_percent = 30.0  # % of oils (used when water_calc_method = "percent")
        self.lye_concentration = 33.0  # % concentration (used when water_calc_method = "concentration")
        self.additives = {}  # {name: weight_in_grams or percent_of_oils}
    
    def add_oil(self, oil_name: str, weight: float):
        """Add or update oil in the recipe"""
        if weight > 0:
            self.oils[oil_name] = weight
        elif oil_name in self.oils:
            del self.oils[oil_name]
    
    def remove_oil(self, oil_name: str):
        """Remove oil from the recipe"""
        if oil_name in self.oils:
            del self.oils[oil_name]
    
    def get_total_oil_weight(self) -> float:
        """Get total weight of all oils"""
        return sum(self.oils.values())
    
    def get_lye_weight(self) -> float:
        """
        Calculate required lye weight based on oils and superfat.
        
        Returns:
            Lye weight in grams
        """
        total_oil = self.get_total_oil_weight()
        if total_oil == 0:
            return 0.0
        
        # Calculate lye needed to saponify all oils
        pure_lye = 0.0
        for oil_name, weight in self.oils.items():
            sap_value = get_oil_sap(oil_name, self.lye_type)
            pure_lye += weight * sap_value
        
        # Apply superfat discount (reduce lye for superfat oils)
        superfat_discount = 1 - (self.superfat_percent / 100)
        lye_weight = pure_lye * superfat_discount
        
        # Adjust for 90% KOH (flakes are only 90% pure)
        if self.lye_type == "90% KOH":
            lye_weight = lye_weight / 0.90
        
        return round(lye_weight, 2)
    
    def get_water_weight(self) -> float:
        """
        Calculate required water weight based on selected method.
        
        Returns:
            Water weight in grams
        """
        total_oil = self.get_total_oil_weight()
        lye_weight = self.get_lye_weight()
        
        if lye_weight == 0:
            return 0.0
        
        # Compute additive-based adjustments (do not mutate state)
        from ..data.additives import ADDITIVES
        additive_adjust = 0.0
        for name, amt in self.additives.items():
            info = ADDITIVES.get(name, {})
            additive_adjust += info.get("water_percent_adjust", 0.0)

        if self.water_calc_method == "ratio":
            # Water-to-Lye Ratio method
            water_weight = lye_weight * self.water_to_lye_ratio
        elif self.water_calc_method == "percent":
            # Water as % of Oils (apply additive adjustments)
            effective_percent = max(0.0, self.water_percent + additive_adjust)
            water_weight = total_oil * (effective_percent / 100)
        elif self.water_calc_method == "concentration":
            # Lye Concentration method: lye/(lye+water) = concentration/100
            # Solved for water: water = lye * (100/concentration - 1)
            if self.lye_concentration > 0 and self.lye_concentration < 100:
                water_weight = lye_weight * ((100 / self.lye_concentration) - 1)
            else:
                water_weight = 0.0
        else:
            water_weight = lye_weight * self.water_to_lye_ratio

        # If any additives are marked as water replacements, treat their grams
        # as part of the water (subtract from the computed water total).
        replacement_total = 0.0
        for name, grams in self.additives.items():
            info = ADDITIVES.get(name, {})
            if info.get("is_water_replacement", False):
                replacement_total += grams

        water_weight = max(0.0, water_weight - replacement_total)

        return round(water_weight, 2)

    def add_additive(self, name: str, amount: float):
        """Add or update an additive. Amount stored in grams."""
        if amount > 0:
            self.additives[name] = amount
        elif name in self.additives:
            del self.additives[name]

    def remove_additive(self, name: str):
        if name in self.additives:
            del self.additives[name]
    
    def get_batch_properties(self) -> Dict[str, float]:
        """
        Calculate batch properties.
        
        Returns:
            Dictionary with various properties
        """
        total_oil = self.get_total_oil_weight()
        lye = self.get_lye_weight()
        water = self.get_water_weight()
        
        total_weight = total_oil + lye + water
        
        # Calculate INS (Iodine Number + Saponification Number)
        # Used to estimate hardness and stability
        iodine_value = self._calculate_iodine_value()
        saponification_number = self._calculate_saponification_number()
        ins_value = saponification_number - iodine_value

        # Fatty acid breakdown (weighted average)
        fa_keys = ["lauric", "myristic", "palmitic", "stearic", "oleic", "linoleic", "linolenic", "ricinoleic"]
        fa_totals = {k: 0.0 for k in fa_keys}
        from ..data.oils import OILS
        for oil_name, weight in self.oils.items():
            info = OILS.get(oil_name, {})
            fa = info.get("fa", {})
            for k in fa_keys:
                fa_val = fa.get(k, 0.0)
                fa_totals[k] += (weight * (fa_val / 100.0))

        fa_percentages = {}
        if total_oil > 0:
            for k in fa_keys:
                fa_percentages[k] = round((fa_totals[k] / total_oil) * 100.0, 2)
        else:
            for k in fa_keys:
                fa_percentages[k] = 0.0
        
        return {
            "total_oil_weight": round(total_oil, 2),
            "lye_weight": lye,
            "water_weight": water,
            "total_batch_weight": round(total_weight, 2),
            "lye_percentage": round((lye / total_oil * 100) if total_oil > 0 else 0, 2),
            "water_percentage": round((water / total_oil * 100) if total_oil > 0 else 0, 2),
            "iodine_value": round(iodine_value, 2),
            "ins_value": round(ins_value, 2),
            "fa_breakdown": fa_percentages,
        }
    
    def _calculate_iodine_value(self) -> float:
        """Calculate total iodine value for the recipe"""
        from ..data.oils import OILS
        
        total_oil = self.get_total_oil_weight()
        if total_oil == 0:
            return 0.0
        
        iodine_sum = 0.0
        for oil_name, weight in self.oils.items():
            if oil_name in OILS:
                iv = OILS[oil_name].get("iodine_value", 0)
                iodine_sum += (weight / total_oil) * iv
        
        return iodine_sum
    
    def _calculate_saponification_number(self) -> float:
        """Calculate saponification number"""
        from ..data.oils import OILS
        
        total_oil = self.get_total_oil_weight()
        if total_oil == 0:
            return 0.0
        
        sap_sum = 0.0
        for oil_name, weight in self.oils.items():
            sap_value = get_oil_sap(oil_name, self.lye_type)
            sap_sum += weight * sap_value
        
        # SAP number in mg KOH per gram oil
        return sap_sum / total_oil * 1000 if total_oil > 0 else 0.0
    
    def scale_recipe(self, new_batch_weight: float):
        """
        Scale the entire recipe to a new total oil weight.
        
        Args:
            new_batch_weight: New total oil weight in grams
        """
        current_total = self.get_total_oil_weight()
        if current_total == 0:
            return
        
        scale_factor = new_batch_weight / current_total
        for oil_name in self.oils:
            self.oils[oil_name] = round(self.oils[oil_name] * scale_factor, 2)
        
        self.total_batch_weight = new_batch_weight
    
    def set_superfat(self, percent: float):
        """Set superfat percentage (typically 0-10%)"""
        self.superfat_percent = max(0, min(100, percent))
    
    def set_water_ratio(self, ratio: float):
        """Set water to lye ratio (typically 1.5-2.5)"""
        self.water_to_lye_ratio = max(0.5, min(5, ratio))
    
    def set_lye_type(self, lye_type: str):
        """Set lye type ('NaOH', 'KOH', or '90% KOH')"""
        if lye_type in ["NaOH", "KOH", "90% KOH"]:
            self.lye_type = lye_type
    
    def set_unit_system(self, unit: str):
        """Set unit system ('grams', 'ounces', 'pounds')"""
        if unit in ["grams", "ounces", "pounds"]:
            self.unit_system = unit
    
    def set_water_calc_method(self, method: str, value: float = None):
        """
        Set water calculation method.
        
        Args:
            method: 'ratio', 'percent', or 'concentration'
            value: The value for the method (ratio, percent, or concentration)
        """
        if method in ["ratio", "percent", "concentration"]:
            self.water_calc_method = method
            if value is not None:
                if method == "ratio":
                    self.water_to_lye_ratio = max(0.5, min(5, value))
                elif method == "percent":
                    self.water_percent = max(0, min(100, value))
                elif method == "concentration":
                    self.lye_concentration = max(1, min(99, value))
    
    def convert_weight(self, weight_grams: float, to_unit: str) -> float:
        """
        Convert weight from grams to target unit.
        
        Args:
            weight_grams: Weight in grams
            to_unit: Target unit ('grams', 'ounces', 'pounds')
        
        Returns:
            Weight in target unit
        """
        if to_unit == "grams":
            return weight_grams
        elif to_unit == "ounces":
            return weight_grams / 28.3495
        elif to_unit == "pounds":
            return weight_grams / 453.592
        return weight_grams
    
    def convert_to_grams(self, weight: float, from_unit: str) -> float:
        """
        Convert weight from any unit to grams.
        
        Args:
            weight: Weight value
            from_unit: Source unit ('grams', 'ounces', 'pounds')
        
        Returns:
            Weight in grams
        """
        if from_unit == "grams":
            return weight
        elif from_unit == "ounces":
            return weight * 28.3495
        elif from_unit == "pounds":
            return weight * 453.592
        return weight
    
    def get_unit_abbreviation(self) -> str:
        """Get abbreviation for current unit system"""
        abbr = {
            "grams": "g",
            "ounces": "oz",
            "pounds": "lbs"
        }
        return abbr.get(self.unit_system, "g")
    
    def get_recipe_dict(self) -> Dict:
        """Get recipe as dictionary for saving"""
        return {
            "oils": self.oils.copy(),
            "superfat_percent": self.superfat_percent,
            "water_to_lye_ratio": self.water_to_lye_ratio,
            "lye_type": self.lye_type,
            "unit_system": self.unit_system,
            "water_calc_method": self.water_calc_method,
            "water_percent": self.water_percent,
            "lye_concentration": self.lye_concentration,
            "properties": self.get_batch_properties()
        }
    
    def load_recipe_dict(self, recipe_data: Dict):
        """Load recipe from dictionary"""
        self.oils = recipe_data.get("oils", {}).copy()
        self.superfat_percent = recipe_data.get("superfat_percent", 5.0)
        self.water_to_lye_ratio = recipe_data.get("water_to_lye_ratio", 2.0)
        self.lye_type = recipe_data.get("lye_type", "NaOH")
        self.unit_system = recipe_data.get("unit_system", "grams")
        self.water_calc_method = recipe_data.get("water_calc_method", "ratio")
        self.water_percent = recipe_data.get("water_percent", 30.0)
        self.lye_concentration = recipe_data.get("lye_concentration", 33.0)
