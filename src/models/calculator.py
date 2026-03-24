"""Calculation models for soap making"""

from typing import Dict, List, Tuple
from ..data.oils import SoapMath


class SoapCalculator:
    """Main calculator for soap recipe calculations"""

    def __init__(self):
        self.oils = {}  # {oil_name: weight_in_grams}
        self.superfat_percent = 5.0  # Default 5% superfat
        self.water_to_lye_ratio = 1.0  # Default 1:1 water to lye
        self.lye_type = "NaOH"  # NaOH, KOH, or 90% KOH
        self.total_batch_weight = 0.0
        self.unit_system = "ounces"  # "grams", "ounces", "pounds"
        self.water_calc_method = "concentration"  # "ratio", "percent", "concentration"
        self.water_percent = 38.0  # % of oils (used when water_calc_method = "percent")
        self.lye_concentration = (
            27.0  # % concentration (used when water_calc_method = "concentration")
        )
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

        # Use SoapMath for exact SoapCalc logic
        # Note: SoapCalc applies superfat as a lye discount
        koh_purity = 0.90 if self.lye_type == "90% KOH" else 1.0
        calc_lye_type = "KOH" if "KOH" in self.lye_type else "NaOH"

        pure_lye = SoapMath.calculate_lye(self.oils, calc_lye_type, koh_purity)

        # Apply superfat (lye discount)
        discount = 1.0 - (self.superfat_percent / 100.0)
        return round(pure_lye * discount, 2)

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
        # Note: SoapCalc logic doesn't typically auto-adjust water for additives in the core math,
        # but we can keep this feature if desired. For strict SoapCalc compliance, we rely on the standard methods.

        method_map = {
            "ratio": "water_lye_ratio",
            "percent": "percent_of_oils",
            "concentration": "lye_concentration",
        }

        method = method_map.get(self.water_calc_method, "percent_of_oils")
        value = 0.0

        if method == "water_lye_ratio":
            value = self.water_to_lye_ratio
        elif method == "percent_of_oils":
            value = self.water_percent
        elif method == "lye_concentration":
            value = self.lye_concentration

        water_weight = SoapMath.calculate_water(total_oil, lye_weight, method, value)

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

        # Fatty acid breakdown (weighted average)
        fa_keys = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "oleic",
            "linoleic",
            "linolenic",
            "ricinoleic",
        ]
        fa_totals = {k: 0.0 for k in fa_keys}
        from ..data.oils import OILS

        for oil_name, weight in self.oils.items():
            info = OILS.get(oil_name, {})
            fa = info.get("fa", {})
            for k in fa_keys:
                fa_val = fa.get(k, 0.0)
                fa_totals[k] += weight * (fa_val / 100.0)

        fa_percentages = {}
        if total_oil > 0:
            for k in fa_keys:
                fa_percentages[k] = round((fa_totals[k] / total_oil) * 100.0, 2)
        else:
            for k in fa_keys:
                fa_percentages[k] = 0.0

        # Compute SoapCalc qualities
        # Note: Standard soap calculators derive qualities solely from the fatty acid
        # profile of the oils. Superfat (lye discount) affects the actual bar
        # (e.g. more conditioning), but does not change these theoretical profile metrics.
        qualities = SoapMath.calculate_qualities(self.oils)

        # Define conversion constants
        GRAMS_TO_OZ = 0.03527396
        GRAMS_TO_LBS = 0.00220462

        # Check what the current unit system is
        if self.unit_system == "ounces":
            total_oil *= GRAMS_TO_OZ
            lye *= GRAMS_TO_OZ
            water *= GRAMS_TO_OZ
            total_weight *= GRAMS_TO_OZ
        elif self.unit_system == "pounds":
            total_oil *= GRAMS_TO_LBS
            lye *= GRAMS_TO_LBS
            water *= GRAMS_TO_LBS
            total_weight *= GRAMS_TO_LBS

        return {
            "total_oil_weight": round(total_oil, 2),
            "lye_weight": round(lye, 3),
            "water_weight": round(water, 2),
            "total_batch_weight": round(total_weight, 2),
            "lye_percentage": round((lye / total_oil * 100) if total_oil > 0 else 0, 2),
            "water_percentage": round(
                (water / total_oil * 100) if total_oil > 0 else 0, 2
            ),
            "fa_breakdown": fa_percentages,
            "relative_qualities": qualities,
            "unit_system": self.get_unit_abbreviation()
        }

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
        unit = str(unit).lower()
        if unit in ["grams", "ounces", "pounds"]:
            self.unit_system = unit
        else:
            self.unit_system = "grams"

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

    def convert_from_grams(self, weight_grams: float, to_unit: str) -> float:
            """ Alias for convert_weight to keep naming consistent with convert_to_grams """
            return self.convert_weight(weight_grams, to_unit)

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

    def _calculate_relative_qualities(self, fa_percentages: dict) -> dict:
        """Deprecated: Use _calculate_recipe_qualities instead.

        This method kept for backward compatibility.
        Calculate qualities from fatty acid percentages (less accurate).
        """
        # Just delegate to the oil-based quality calculation
        return SoapMath.calculate_qualities(self.oils)

    def get_unit_abbreviation(self):
        mapping = {
            "grams": "g",
            "ounces": "oz",
            "pounds": "lb"
        }
        # Using .get() ensures that if self.unit_system is "Ounces" (Capitalized)
        # or missing, it defaults to "g" instead of None.
        return mapping.get(self.unit_system, "g")

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
            "properties": self.get_batch_properties(),
        }

    def load_recipe_dict(self, recipe_data: Dict):
        """Load recipe from dictionary"""
        self.recipe_name = recipe_data.get("name", "Untitled Recipe")
        self.oils = recipe_data.get("oils", {}).copy()
        self.superfat_percent = recipe_data.get("superfat_percent", 5.0)
        self.water_to_lye_ratio = recipe_data.get("water_to_lye_ratio", 2.0)
        self.lye_type = recipe_data.get("lye_type", "NaOH")
        self.water_calc_method = recipe_data.get("water_calc_method", "ratio")
        self.water_percent = recipe_data.get("water_percent", 30.0)
        self.lye_concentration = recipe_data.get("lye_concentration", 33.0)

        # Force the calculator to use the unit saved in the recipe
        self.unit_system = recipe_data.get("unit_system", "ounces").lower()

    def get_recipe_data(self) -> dict:
        """Returns data formatted for the Recipe model:

        """
        return {
            "name": getattr(self, 'recipe_name', "New Recipe"),
            "unit_system": self.unit_system,
            "oils": self.oils,
            "superfat_percent": self.superfat_percent,
            "water_to_lye_ratio": self.water_to_lye_ratio,
            "lye_type": self.lye_type,
            "batch_weight": self.total_batch_weight,
            "water_calc_method": self.water_calc_method,
            "water_percent": self.water_percent,
            "lye_concentration": self.lye_concentration,
            "additives": self.additives,

        }

    def calculate_masterbatch_pour(self, target_lye_grams, mb_concentration=50.0, final_target_conc=33.3):
        """
        mb_concentration: The concentration of your premixed lye (usually 50.0)
        final_target_conc: What you want the final soap to be (e.g. 33.3 for a 2:1)
        """
        # 1. Total weight of the 50/50 solution needed to get the required dry lye
        # If you need 100g lye, you need 200g of 50/50 solution.
        total_mb_pour = target_lye_grams / (mb_concentration / 100)

        # 2. Total water required for the FINAL target concentration
        # Formula: Total Water = (Lye / Conc) - Lye
        total_required_water = (target_lye_grams / (final_target_conc / 100)) - target_lye_grams

        # 3. Water already present in your masterbatch pour
        water_in_mb = total_mb_pour - target_lye_grams

        # 4. Additional water to add to the oils
        extra_water = total_required_water - water_in_mb

        return {
            "mb_liquid_pour": total_mb_pour,
            "extra_water_to_add": max(0, extra_water)
        }


    def rebalance_oils(self, edited_name: str, new_percentage: float):
        """
        Adjusts all UNLOCKED oils proportionally when one percentage is edited,
        maintaining the total batch weight.
        """
        if not self.oils or self.get_total_oil_weight() <= 0:
            return

        if not hasattr(self, 'locked_oils'):
            self.locked_oils = set()

        # 1. Capture the current total weight we need to maintain
        target_total_weight = self.get_total_oil_weight()

        # 2. Convert current weights (grams) to percentages
        current_percentages = {
            name: (weight / target_total_weight * 100)
            for name, weight in self.oils.items()
        }

        # 3. Calculate the Delta (difference in percentage)
        old_percentage = current_percentages.get(edited_name, 0)
        delta = new_percentage - old_percentage

        # 4. Update the edited oil's percentage
        current_percentages[edited_name] = new_percentage

        # 5. Identify adjustable oils (not edited, not locked)
        adjustable_names = [
            name for name in self.oils.keys()
            if name != edited_name and name not in self.locked_oils
        ]

        total_adjustable_pct = sum(current_percentages[name] for name in adjustable_names)

        # 6. Redistribute the delta across adjustable oils
        if total_adjustable_pct > 0:
            for name in adjustable_names:
                share = current_percentages[name] / total_adjustable_pct
                current_percentages[name] -= delta * share
        elif adjustable_names:
            # Fallback: if other oils were at 0%, split the delta equally
            split_delta = delta / len(adjustable_names)
            for name in adjustable_names:
                current_percentages[name] -= split_delta

        # 7. Convert percentages back to weights and update self.oils
        for name, pct in current_percentages.items():
            # Clamp to 0-100 and calculate weight
            final_pct = max(0, min(100, pct))
            self.oils[name] = round((final_pct / 100) * target_total_weight, 2)
            """
            Adjusts all UNLOCKED oils proportionally when one is edited.
            """
            if not hasattr(self, 'locked_oils'):
                self.locked_oils = set()

            # 1. Calculate the change (Delta)
            old_percentage = self.oils.get(edited_name, 0) # Adjust based on your dict key
            delta = new_percentage - old_percentage

            # 2. Update the edited oil
            self.oils[edited_name] = new_percentage

            # 3. Identify candidates for adjustment (Not the one edited, not locked)
            adjustable_oils = [
                name for name in self.oils.keys()
                if name != edited_name and name not in self.locked_oils
            ]

            total_adjustable_pct = sum(self.oils[name] for name in adjustable_oils)

            # 4. Redistribute the delta
            if total_adjustable_pct > 0:
                for name in adjustable_oils:
                    share = self.oils[name] / total_adjustable_pct
                    self.oils[name] -= delta * share

            # Ensure no negative percentages (clamping)
            for name in self.oils:
                self.oils[name] = max(0, self.oils[name])