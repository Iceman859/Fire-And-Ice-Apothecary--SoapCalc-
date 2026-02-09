"""Oil database with saponification (SAP) values and quality metrics"""

# Oil database with SAP values
# SAP value = mg of NaOH needed per gram of oil
# All values are standard soap making references

OILS = {
    # Carrier Oils
    "Coconut Oil": {
        "sap_naoh": 0.183,
        "sap_koh": 0.256,
        "iodine_value": 8,
        "hardness": 8,
        "description": "Creates hard bar soap, high lather, can be drying. Industry standard FA profile.",
        "quality_hardness": 7.6,
        "quality_fluffy": 9.5,
        "quality_stable": 0.7,
        "quality_moisturizing": 2.0,
        "fa": {
            "lauric": 47.0,
            "myristic": 18.5,
            "palmitic": 9.0,
            "stearic": 3.0,
            "oleic": 6.0,
            "linoleic": 1.5,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Palm Oil": {
        "sap_naoh": 0.141,
        "sap_koh": 0.196,
        "iodine_value": 53,
        "hardness": 5,
        "description": "Creates hard bar soap, moderate lather",
        "quality_hardness": 6.6,
        "quality_fluffy": 3.8,
        "quality_stable": 6.9,
        "quality_moisturizing": 6.3,
        "fa": {
            "lauric": 0.5,
            "myristic": 1.0,
            "palmitic": 44.0,
            "stearic": 5.0,
            "oleic": 39.0,
            "linoleic": 10.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Olive Oil": {
        "sap_naoh": 0.134,
        "sap_koh": 0.187,
        "iodine_value": 80,
        "hardness": 1,
        "description": "Produces creamy lather, mild soap. Extra virgin/virgin average.",
        "quality_hardness": 5.2,
        "quality_fluffy": 3.1,
        "quality_stable": 8.0,
        "quality_moisturizing": 8.7,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 10.5,
            "stearic": 2.5,
            "oleic": 71.2,
            "linoleic": 10.0,
            "linolenic": 0.8,
            "ricinoleic": 0.0
        }
    },
    "Canola Oil": {
        "sap_naoh": 0.124,
        "sap_koh": 0.173,
        "iodine_value": 103,
        "hardness": 1,
        "description": "Creates soft soap, conditioning",
        "quality_hardness": 3.6,
        "quality_fluffy": 2.7,
        "quality_stable": 7.8,
        "quality_moisturizing": 9.3,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 4.0,
            "stearic": 2.0,
            "oleic": 62.0,
            "linoleic": 20.0,
            "linolenic": 10.0,
            "ricinoleic": 0.0
        }
    },
    "Soybean Oil": {
        "sap_naoh": 0.136,
        "sap_koh": 0.190,
        "iodine_value": 130,
        "hardness": 1,
        "description": "Produces soft soap, conditioning properties",
        "quality_hardness": 3.0,
        "quality_fluffy": 2.8,
        "quality_stable": 7.0,
        "quality_moisturizing": 8.2,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 10.0,
            "stearic": 4.0,
            "oleic": 24.0,
            "linoleic": 50.0,
            "linolenic": 6.0,
            "ricinoleic": 0.0
        }
    },
    "Sunflower Oil": {
        "sap_naoh": 0.134,
        "sap_koh": 0.187,
        "iodine_value": 130,
        "hardness": 1,
        "description": "Creates soft soap, nice lather",
        "quality_hardness": 2.8,
        "quality_fluffy": 2.4,
        "quality_stable": 6.3,
        "quality_moisturizing": 7.9,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 5.0,
            "stearic": 6.0,
            "oleic": 20.0,
            "linoleic": 65.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Coconut Oil (Refined)": {
        "sap_naoh": 0.183,
        "sap_koh": 0.256,
        "iodine_value": 8,
        "hardness": 8,
        "description": "Refined version of coconut oil",
        "quality_hardness": 7.6,
        "quality_fluffy": 9.5,
        "quality_stable": 0.7,
        "quality_moisturizing": 2.0,
        "fa": {
            "lauric": 48.0,
            "myristic": 18.0,
            "palmitic": 9.0,
            "stearic": 3.0,
            "oleic": 7.0,
            "linoleic": 2.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Palm Kernel Oil": {
        "sap_naoh": 0.156,
        "sap_koh": 0.218,
        "iodine_value": 37,
        "hardness": 7,
        "description": "Similar to coconut, creates hard bar",
        "quality_hardness": 8.0,
        "quality_fluffy": 8.9,
        "quality_stable": 1.6,
        "quality_moisturizing": 2.9,
        "fa": {
            "lauric": 48.0,
            "myristic": 15.0,
            "palmitic": 9.0,
            "stearic": 4.0,
            "oleic": 6.0,
            "linoleic": 0.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    # Premium Oils
    "Avocado Oil": {
        "sap_naoh": 0.133,
        "sap_koh": 0.186,
        "iodine_value": 100,
        "hardness": 1,
        "description": "Conditioning and moisturizing",
        "quality_hardness": 5.1,
        "quality_fluffy": 3.7,
        "quality_stable": 7.3,
        "quality_moisturizing": 8.5,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 14.0,
            "stearic": 2.0,
            "oleic": 63.0,
            "linoleic": 11.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Castor Oil": {
        "sap_naoh": 0.129,
        "sap_koh": 0.180,
        "iodine_value": 85,
        "hardness": 1,
        "description": "Increases lather, conditioning. Unique ricinoleic acid structure.",
        "quality_hardness": 4.4,
        "quality_fluffy": 1.3,
        "quality_stable": 10.0,
        "quality_moisturizing": 10.0,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 1.5,
            "stearic": 2.0,
            "oleic": 5.0,
            "linoleic": 2.5,
            "linolenic": 0.0,
            "ricinoleic": 88.0
        }
    },
    "Jojoba Oil": {
        "sap_naoh": 0.069,
        "sap_koh": 0.097,
        "iodine_value": 82,
        "hardness": 1,
        "description": "Premium conditioning oil",
        "quality_hardness": 3.3,
        "quality_fluffy": 0.3,
        "quality_stable": 1.0,
        "quality_moisturizing": 6.1,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 5.0,
            "stearic": 1.0,
            "oleic": 73.0,
            "linoleic": 8.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Sweet Almond Oil": {
        "sap_naoh": 0.136,
        "sap_koh": 0.191,
        "iodine_value": 97,
        "hardness": 1,
        "description": "Conditioning and moisturizing",
        "quality_hardness": 4.0,
        "quality_fluffy": 2.5,
        "quality_stable": 7.9,
        "quality_moisturizing": 9.0,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 6.0,
            "stearic": 3.0,
            "oleic": 62.0,
            "linoleic": 24.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Argan Oil": {
        "sap_naoh": 0.136,
        "sap_koh": 0.190,
        "iodine_value": 94,
        "hardness": 1,
        "description": "Luxury conditioning oil",
        "quality_hardness": 4.4,
        "quality_fluffy": 3.0,
        "quality_stable": 7.8,
        "quality_moisturizing": 8.5,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 12.0,
            "stearic": 5.0,
            "oleic": 46.0,
            "linoleic": 28.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Shea Butter": {
        "sap_naoh": 0.128,
        "sap_koh": 0.179,
        "iodine_value": 59,
        "hardness": 4,
        "description": "Rich and creamy, conditioning. Refined grade average.",
        "quality_hardness": 6.5,
        "quality_fluffy": 2.7,
        "quality_stable": 8.2,
        "quality_moisturizing": 6.9,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 3.5,
            "stearic": 42.0,
            "oleic": 44.5,
            "linoleic": 6.5,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Cocoa Butter": {
        "sap_naoh": 0.137,
        "sap_koh": 0.192,
        "iodine_value": 35,
        "hardness": 6,
        "description": "Hard and stable, excellent conditioning",
        "quality_hardness": 7.7,
        "quality_fluffy": 3.2,
        "quality_stable": 7.4,
        "quality_moisturizing": 5.4,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 25.0,
            "stearic": 36.0,
            "oleic": 35.0,
            "linoleic": 3.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    # Specialty Oils
    "Grapeseed Oil": {
        "sap_naoh": 0.128,
        "sap_koh": 0.179,
        "iodine_value": 140,
        "hardness": 1,
        "description": "Lightweight, conditioning",
        "quality_hardness": 3.0,
        "quality_fluffy": 3.0,
        "quality_stable": 7.9,
        "quality_moisturizing": 9.4,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 5.0,
            "stearic": 3.0,
            "oleic": 16.0,
            "linoleic": 68.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Hemp Oil": {
        "sap_naoh": 0.127,
        "sap_koh": 0.178,
        "iodine_value": 161,
        "hardness": 1,
        "description": "Conditioning and moisturizing",
        "quality_hardness": 1.6,
        "quality_fluffy": 3.0,
        "quality_stable": 7.8,
        "quality_moisturizing": 9.1,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 7.0,
            "stearic": 3.0,
            "oleic": 12.0,
            "linoleic": 55.0,
            "linolenic": 23.0,
            "ricinoleic": 0.0
        }
    },
    "Corn Oil": {
        "sap_naoh": 0.136,
        "sap_koh": 0.190,
        "iodine_value": 103,
        "hardness": 1,
        "description": "Creates soft soap with lather",
        "quality_hardness": 3.8,
        "quality_fluffy": 3.2,
        "quality_stable": 7.9,
        "quality_moisturizing": 8.9,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 12.0,
            "stearic": 2.0,
            "oleic": 30.0,
            "linoleic": 50.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Sea Buckthorn Oil": {
        "sap_naoh": 0.150,
        "sap_koh": 0.209,
        "iodine_value": 126,
        "hardness": 1,
        "description": "Rich in vitamins and antioxidants",
        "quality_hardness": 0.0,
        "quality_fluffy": 0.0,
        "quality_stable": 0.0,
        "quality_moisturizing": 0.0,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 6.0,
            "stearic": 1.0,
            "oleic": 18.0,
            "linoleic": 29.0,
            "linolenic": 1.0,
            "ricinoleic": 0.0
        }
    },
    "Rice Bran Oil": {
        "sap_naoh": 0.133,
        "sap_koh": 0.186,
        "iodine_value": 100,
        "hardness": 1,
        "description": "Stable oil, conditioning and skin-friendly",
        "quality_hardness": 4.0,
        "quality_fluffy": 3.2,
        "quality_stable": 7.9,
        "quality_moisturizing": 9.0,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 20.0,
            "stearic": 1.0,
            "oleic": 45.0,
            "linoleic": 30.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Sesame Oil": {
        "sap_naoh": 0.135,
        "sap_koh": 0.188,
        "iodine_value": 103,
        "hardness": 1,
        "description": "Conditioning, used in many traditional recipes",
        "quality_hardness": 3.9,
        "quality_fluffy": 2.9,
        "quality_stable": 7.7,
        "quality_moisturizing": 8.7,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 9.0,
            "stearic": 4.0,
            "oleic": 40.0,
            "linoleic": 46.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Flaxseed Oil (Linseed)": {
        "sap_naoh": 0.135,
        "sap_koh": 0.188,
        "iodine_value": 175,
        "hardness": 0,
        "description": "Very high in linolenic acid; makes soft soap",
        "quality_hardness": 3.7,
        "quality_fluffy": 2.9,
        "quality_stable": 7.5,
        "quality_moisturizing": 8.9,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 7.0,
            "stearic": 2.0,
            "oleic": 20.0,
            "linoleic": 16.0,
            "linolenic": 50.0,
            "ricinoleic": 0.0
        }
    },
    "Walnut Oil": {
        "sap_naoh": 0.136,
        "sap_koh": 0.190,
        "iodine_value": 140,
        "hardness": 1,
        "description": "Conditioning, rich in omega fatty acids",
        "quality_hardness": 2.3,
        "quality_fluffy": 2.6,
        "quality_stable": 6.9,
        "quality_moisturizing": 8.3,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 6.0,
            "stearic": 2.0,
            "oleic": 20.0,
            "linoleic": 58.0,
            "linolenic": 10.0,
            "ricinoleic": 0.0
        }
    },
    "Peanut Oil": {
        "sap_naoh": 0.137,
        "sap_koh": 0.191,
        "iodine_value": 95,
        "hardness": 1,
        "description": "Good conditioning, common in soap recipes",
        "quality_hardness": 4.5,
        "quality_fluffy": 2.9,
        "quality_stable": 7.4,
        "quality_moisturizing": 8.4,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 9.0,
            "stearic": 3.0,
            "oleic": 48.0,
            "linoleic": 34.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
    "Safflower Oil": {
        "sap_naoh": 0.132,
        "sap_koh": 0.183,
        "iodine_value": 140,
        "hardness": 1,
        "description": "High linoleic variety is conditioning",
        "quality_hardness": 3.7,
        "quality_fluffy": 3.0,
        "quality_stable": 8.0,
        "quality_moisturizing": 9.2,
        "fa": {
            "lauric": 0.0,
            "myristic": 0.0,
            "palmitic": 6.0,
            "stearic": 2.0,
            "oleic": 10.0,
            "linoleic": 82.0,
            "linolenic": 0.0,
            "ricinoleic": 0.0
        }
    },
}

def get_oil_sap(oil_name: str, lye_type: str = "NaOH") -> float:
    """Get SAP value for an oil."""
    if oil_name not in OILS:
        return 0.0
    key = f"sap_{lye_type.lower()}"
    return OILS[oil_name].get(key, 0.0)

def get_all_oil_names() -> list:
    """Get list of all available oil names"""
    return sorted(list(OILS.keys()))

def get_oil_info(oil_name: str) -> dict:
    """Get full information about an oil"""
    return OILS.get(oil_name, {})