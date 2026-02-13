"""Additives database used for recipe modifiers"""
import json
import os

ADDITIVES = {
    "Goat Milk (Liquid)": {
        "description": "Fresh or reconstituted milk. Replaces water in the recipe.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 0.0,
        "is_water_replacement": True  # Subtracts from calculated water amount
    },
    "Goat Milk (Powder)": {
        "description": "Powdered milk added to trace or oils. Does not replace water.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 1.0,
        "is_water_replacement": False
    },
    "Coconut Milk (Liquid)": {
        "description": "Liquid coconut milk. Replaces water.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 0.0,
        "is_water_replacement": True
    },
    "Honey": {
        "description": "Adds conditioning and attracts moisture; may darken soap.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 2.0,
        "is_water_replacement": False
    },
    "Sugar": {
        "description": "Small amounts improve lather in soap.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 1.0,
        "is_water_replacement": False
    },
    "Salt": {
        "description": "Adds hardness to the bar.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 1.0,
        "is_water_replacement": False
    },
    "Kaolin Clay": {
        "description": "A mild clay used for texture and color.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 1.0,
        "is_water_replacement": False
    },
    "Sodium Lactate": {
        "description": "Liquid salt derived from corn/beets. Hardens soap significantly.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 3.0,
        "is_water_replacement": False
    },
    "Fragrance / Essential Oil": {
        "description": "Scent. Usage rates vary widely (typically 3-6%).",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 3.0,
        "is_water_replacement": False
    }
}

CUSTOM_ADDITIVES_FILE = "custom_additives.json"


def get_all_additive_names():
    return sorted(list(ADDITIVES.keys()))


def get_additive_info(name: str) -> dict:
    return ADDITIVES.get(name, {})


def add_additive_entry(name: str, info: dict):
    """Add or update an additive entry in the ADDITIVES DB."""
    ADDITIVES[name] = info
    
    # Load existing custom additives
    custom_additives = {}
    if os.path.exists(CUSTOM_ADDITIVES_FILE):
        try:
            with open(CUSTOM_ADDITIVES_FILE, 'r') as f:
                custom_additives = json.load(f)
        except Exception:
            pass
    
    custom_additives[name] = info
    
    try:
        with open(CUSTOM_ADDITIVES_FILE, 'w') as f:
            json.dump(custom_additives, f, indent=4)
    except Exception as e:
        print(f"Error saving custom additive: {e}")


def remove_additive_entry(name: str):
    if name in ADDITIVES:
        del ADDITIVES[name]
        
    custom_additives = {}
    if os.path.exists(CUSTOM_ADDITIVES_FILE):
        try:
            with open(CUSTOM_ADDITIVES_FILE, 'r') as f:
                custom_additives = json.load(f)
        except Exception:
            pass
            
    if name in custom_additives:
        del custom_additives[name]
        try:
            with open(CUSTOM_ADDITIVES_FILE, 'w') as f:
                json.dump(custom_additives, f, indent=4)
        except Exception as e:
            print(f"Error deleting custom additive: {e}")

# Load custom additives on import
if os.path.exists(CUSTOM_ADDITIVES_FILE):
    try:
        with open(CUSTOM_ADDITIVES_FILE, 'r') as f:
            custom_data = json.load(f)
            ADDITIVES.update(custom_data)
    except Exception as e:
        print(f"Error loading custom additives: {e}")