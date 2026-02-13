"""
Database of ingredients used in Gummy manufacturing.
"""

GUMMY_INGREDIENTS = {
    "Gelatin (250 Bloom)": {
        "type": "gelling",
        "solids": 88.0,
        "bloom": 250,
        "description": "High strength gelatin for firm chew."
    },
    "Gelatin (160 Bloom)": {
        "type": "gelling",
        "solids": 88.0,
        "bloom": 160,
        "description": "Lower strength gelatin for softer chew."
    },
    "Gelatin (225 Bloom)": {
        "type": "gelling",
        "solids": 88.0,
        "bloom": 225,
        "description": "High-medium strength gelatin (e.g., Gold)."
    },
    "Sugar (Sucrose)": {
        "type": "sweetener",
        "solids": 100.0,
        "description": "Standard granulated sugar."
    },
    "Corn Syrup (43 DE)": {
        "type": "sweetener",
        "solids": 80.0,
        "description": "Glucose syrup, prevents crystallization."
    },
    "Water": {
        "type": "liquid",
        "solids": 0.0,
        "description": "For hydration."
    },
    "Fruit Juice": {
        "type": "liquid",
        "solids": 12.0,
        "description": "Standard fruit juice (approx 12 Brix)."
    },
    "Citric Acid": {
        "type": "acid",
        "solids": 100.0,
        "description": "Acidulant for flavor and pectin setting."
    },
    "Sorbitol (70%)": {
        "type": "humectant",
        "solids": 70.0,
        "description": "Humectant to maintain texture."
    },
    "Pectin (HM)": {
        "type": "gelling",
        "solids": 100.0,
        "description": "High Methoxyl Pectin, requires acid and sugar to set."
    }
}

def get_all_gummy_ingredients():
    return sorted(GUMMY_INGREDIENTS.keys())