"""Basic tests for SoapCalc core functionality"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import SoapCalculator, Recipe, RecipeManager
from src.data import get_all_oil_names, get_oil_sap


def test_calculator():
    """Test basic calculator functionality"""
    calc = SoapCalculator()
    
    # Add some oils
    calc.add_oil("Coconut Oil", 200)
    calc.add_oil("Olive Oil", 300)
    calc.add_oil("Palm Oil", 500)
    
    total_oil = calc.get_total_oil_weight()
    assert total_oil == 1000, f"Expected 1000g, got {total_oil}g"
    
    # Get calculations
    lye = calc.get_lye_weight()
    water = calc.get_water_weight()
    
    assert lye > 0, "Lye weight should be > 0"
    assert water > 0, "Water weight should be > 0"
    
    # Get batch properties
    props = calc.get_batch_properties()
    assert "ins_value" in props, "Missing INS value"
    assert "iodine_value" in props, "Missing iodine value"
    
    print(f"✓ Calculator test passed")
    print(f"  Total oil: {total_oil}g")
    print(f"  Lye needed: {lye}g")
    print(f"  Water needed: {water}g")
    print(f"  INS value: {props['ins_value']}")


def test_recipe():
    """Test recipe save/load functionality"""
    recipe = Recipe("Test Recipe")
    recipe.oils = {"Coconut Oil": 200, "Olive Oil": 300}
    recipe.superfat_percent = 5.0
    recipe.lye_type = "NaOH"
    
    # Convert to dict and back
    data = recipe.to_dict()
    loaded = Recipe.from_dict(data)
    
    assert loaded.name == "Test Recipe", "Recipe name mismatch"
    assert loaded.oils == recipe.oils, "Oils mismatch"
    assert loaded.superfat_percent == 5.0, "Superfat mismatch"
    
    print(f"✓ Recipe test passed")


def test_oils_database():
    """Test oils database"""
    oils = get_all_oil_names()
    assert len(oils) > 0, "Oil database is empty"
    
    # Test SAP values
    sap_naoh = get_oil_sap("Coconut Oil", "NaOH")
    sap_koh = get_oil_sap("Coconut Oil", "KOH")
    
    assert sap_naoh > 0, "NaOH SAP value invalid"
    assert sap_koh > sap_naoh, "KOH SAP should be higher than NaOH"
    
    print(f"✓ Oil database test passed")
    print(f"  Total oils in database: {len(oils)}")
    print(f"  Coconut Oil NaOH SAP: {sap_naoh}")
    print(f"  Coconut Oil KOH SAP: {sap_koh}")


def test_scaling():
    """Test recipe scaling"""
    calc = SoapCalculator()
    calc.add_oil("Coconut Oil", 200)
    calc.add_oil("Olive Oil", 300)
    
    original_total_oil = calc.get_total_oil_weight()
    original_lye = calc.get_lye_weight()
    
    # Scale to 2000g (from 500g = 4x)
    calc.scale_recipe(2000)
    
    new_total_oil = calc.get_total_oil_weight()
    new_lye = calc.get_lye_weight()
    
    # Total oil should be exactly 2000g
    assert new_total_oil == 2000, f"Expected 2000g total oil, got {new_total_oil}g"
    
    # Lye should scale proportionally (4x in this case)
    expected_lye = original_lye * 4
    tolerance = expected_lye * 0.02  # 2% tolerance
    assert abs(new_lye - expected_lye) <= tolerance, f"Scaling error: expected ~{expected_lye}g, got {new_lye}g"
    
    print(f"✓ Scaling test passed")
    print(f"  Original: {original_total_oil}g oils, {original_lye}g lye")
    print(f"  Scaled: {new_total_oil}g oils, {new_lye}g lye")


if __name__ == "__main__":
    print("Running SoapCalc tests...\n")
    
    try:
        test_oils_database()
        test_calculator()
        test_recipe()
        test_scaling()
        
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
