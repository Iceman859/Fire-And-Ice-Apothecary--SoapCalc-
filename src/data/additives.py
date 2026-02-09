"""Additives database used for recipe modifiers"""

ADDITIVES = {
    "Goat Milk": {
        "description": "Powdered or liquid milk. Often used as a partial water replacement for more conditioned bars.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 5.0,
        "is_water_replacement": True  # when added (grams) treat as part of water
    },
    "Honey": {
        "description": "Adds conditioning and attracts moisture; may darken soap.",
        "water_percent_adjust": 5.0,
        "default_percent_of_oils": 2.0
    },
    "Sugar": {
        "description": "Small amounts improve lather in soap.",
        "water_percent_adjust": 0.0,
        "default_percent_of_oils": 1.0
    },
    "Kaolin Clay": {
        "description": "A mild clay used for texture and color; reduces available water slightly.",
        "water_percent_adjust": -3.0,
        "default_percent_of_oils": 3.0
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
