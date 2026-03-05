"""
Default ingredient data for candy making.
"""

CANDY_INGREDIENTS = {
    "Sugar": {},
    "Water": {},
    "Corn Syrup": {},
    "Gelatin": {},
    "Citric Acid": {},
    "Flavoring": {},
    "Food Coloring": {},
}


def get_all_candy_ingredient_names():
    """Returns a sorted list of all candy ingredient names."""
    return sorted(CANDY_INGREDIENTS.keys())
