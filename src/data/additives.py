"""Additives database used for recipe modifiers"""

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


def get_all_additive_names():
    return sorted(list(ADDITIVES.keys()))


def get_additive_info(name: str) -> dict:
    return ADDITIVES.get(name, {})


def add_additive_entry(name: str, info: dict):
    """Add or update an additive entry in the ADDITIVES DB."""
    ADDITIVES[name] = info


def remove_additive_entry(name: str):
    if name in ADDITIVES:
        del ADDITIVES[name]


