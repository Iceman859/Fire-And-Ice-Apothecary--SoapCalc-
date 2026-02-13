"""
Oil database and calculation logic derived from SoapCalc.
Contains exact SAP values, Fatty Acid profiles, and Quality calculation algorithms.
"""
import json
import os

# Helper to calculate qualities based on SoapCalc logic
def _calc_qualities(fa, override=None):
    if override:
        return override
    
    # Standard SoapCalc Formulas derived from soapcalc.js getProperties()
    # Hardness = Lauric + Myristic + Palmitic + Stearic
    # Cleansing = Lauric + Myristic
    # Bubbly = Lauric + Myristic + Ricinoleic
    # Creamy = Palmitic + Stearic + Ricinoleic
    # Conditioning = Ricinoleic + Oleic + Linoleic + Linolenic
    
    return {
        "hardness": fa.get("lauric",0) + fa.get("myristic",0) + fa.get("palmitic",0) + fa.get("stearic",0),
        "cleansing": fa.get("lauric",0) + fa.get("myristic",0),
        "bubbly": fa.get("lauric",0) + fa.get("myristic",0) + fa.get("ricinoleic",0),
        "creamy": fa.get("palmitic",0) + fa.get("stearic",0) + fa.get("ricinoleic",0),
        "conditioning": fa.get("ricinoleic",0) + fa.get("oleic",0) + fa.get("linoleic",0) + fa.get("linolenic",0)
    }

# Full Database from soapcalc.js
# SAP values in JS are KOH. NaOH = KOH * (40/56.1)
OILS = {
    "Abyssinian Oil": {
        "sap_koh": 0.168, "sap_naoh": 0.120, "iodine": 98, "ins": 70,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 2, "ricinoleic": 0, "oleic": 18, "linoleic": 11, "linolenic": 4},
        "qualities": {"hardness": 6, "cleansing": 0, "bubbly": 0, "creamy": 80, "conditioning": 94} # Exception ID 145
    },
    "Almond Butter": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 70, "ins": 118,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 9, "stearic": 15, "ricinoleic": 0, "oleic": 58, "linoleic": 16, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 9, "stearic": 15, "ricinoleic": 0, "oleic": 58, "linoleic": 16, "linolenic": 0})
    },
    "Almond Oil, sweet": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 99, "ins": 97,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 0, "ricinoleic": 0, "oleic": 71, "linoleic": 18, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 0, "ricinoleic": 0, "oleic": 71, "linoleic": 18, "linolenic": 0})
    },
    "Aloe Butter": {
        "sap_koh": 0.240, "sap_naoh": 0.171, "iodine": 9, "ins": 241,
        "fa": {"lauric": 45, "myristic": 18, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 7, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 45, "myristic": 18, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 7, "linoleic": 2, "linolenic": 0})
    },
    "Andiroba Oil,karaba,crabwood": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 68, "ins": 120,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 28, "stearic": 8, "ricinoleic": 0, "oleic": 51, "linoleic": 9, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 28, "stearic": 8, "ricinoleic": 0, "oleic": 51, "linoleic": 9, "linolenic": 0})
    },
    "Apricot Kernal Oil": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 100, "ins": 91,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 0, "ricinoleic": 0, "oleic": 66, "linoleic": 27, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 0, "ricinoleic": 0, "oleic": 66, "linoleic": 27, "linolenic": 0})
    },
    "Argan Oil": {
        "sap_koh": 0.191, "sap_naoh": 0.136, "iodine": 95, "ins": 95,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 14, "stearic": 0, "ricinoleic": 0, "oleic": 46, "linoleic": 34, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 14, "stearic": 0, "ricinoleic": 0, "oleic": 46, "linoleic": 34, "linolenic": 1})
    },
    "Avocado butter": {
        "sap_koh": 0.187, "sap_naoh": 0.133, "iodine": 67, "ins": 120,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 21, "stearic": 10, "ricinoleic": 0, "oleic": 53, "linoleic": 6, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 21, "stearic": 10, "ricinoleic": 0, "oleic": 53, "linoleic": 6, "linolenic": 2})
    },
    "Avocado Oil": {
        "sap_koh": 0.186, "sap_naoh": 0.133, "iodine": 86, "ins": 99,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 20, "stearic": 2, "ricinoleic": 0, "oleic": 58, "linoleic": 12, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 20, "stearic": 2, "ricinoleic": 0, "oleic": 58, "linoleic": 12, "linolenic": 0})
    },
    "Babassu Oil": {
        "sap_koh": 0.245, "sap_naoh": 0.175, "iodine": 15, "ins": 230,
        "fa": {"lauric": 50, "myristic": 20, "palmitic": 11, "stearic": 4, "ricinoleic": 0, "oleic": 10, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 50, "myristic": 20, "palmitic": 11, "stearic": 4, "ricinoleic": 0, "oleic": 10, "linoleic": 0, "linolenic": 0})
    },
    "Baobab Oil": {
        "sap_koh": 0.200, "sap_naoh": 0.143, "iodine": 75, "ins": 125,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 24, "stearic": 4, "ricinoleic": 0, "oleic": 37, "linoleic": 28, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 24, "stearic": 4, "ricinoleic": 0, "oleic": 37, "linoleic": 28, "linolenic": 2})
    },
    "Beeswax": {
        "sap_koh": 0.094, "sap_naoh": 0.067, "iodine": 10, "ins": 84,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": {"hardness": 90, "cleansing": 0, "bubbly": 0, "creamy": 50, "conditioning": 50} # Exception ID 5
    },
    "Black Cumin Seed Oil, nigella sativa": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 133, "ins": 62,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 3, "ricinoleic": 0, "oleic": 22, "linoleic": 60, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 3, "ricinoleic": 0, "oleic": 22, "linoleic": 60, "linolenic": 1})
    },
    "Black Current Seed Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 178, "ins": 12,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 13, "linoleic": 46, "linolenic": 29},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 13, "linoleic": 46, "linolenic": 29})
    },
    "Borage Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 135, "ins": 55,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 4, "ricinoleic": 0, "oleic": 20, "linoleic": 43, "linolenic": 5},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 4, "ricinoleic": 0, "oleic": 20, "linoleic": 43, "linolenic": 5})
    },
    "Brazil Nut Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 100, "ins": 90,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 11, "ricinoleic": 0, "oleic": 39, "linoleic": 36, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 11, "ricinoleic": 0, "oleic": 39, "linoleic": 36, "linolenic": 0})
    },
    "Broccoli Seed Oil, Brassica Oleracea": {
        "sap_koh": 0.172, "sap_naoh": 0.123, "iodine": 105, "ins": 67,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 1, "ricinoleic": 0, "oleic": 14, "linoleic": 11, "linolenic": 9},
        "qualities": {"hardness": 7, "cleansing": 0, "bubbly": 0, "creamy": 6, "conditioning": 93} # Exception ID 138
    },
    "Buriti Oil": {
        "sap_koh": 0.223, "sap_naoh": 0.159, "iodine": 70, "ins": 153,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 17, "stearic": 2, "ricinoleic": 0, "oleic": 71, "linoleic": 7, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 17, "stearic": 2, "ricinoleic": 0, "oleic": 71, "linoleic": 7, "linolenic": 1})
    },
    "Camelina Seed Oil": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 144, "ins": 44,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 24, "linoleic": 19, "linolenic": 45},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 24, "linoleic": 19, "linolenic": 45})
    },
    "Camellia Oil, Tea Seed": {
        "sap_koh": 0.193, "sap_naoh": 0.138, "iodine": 78, "ins": 115,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 2, "ricinoleic": 0, "oleic": 77, "linoleic": 8, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 2, "ricinoleic": 0, "oleic": 77, "linoleic": 8, "linolenic": 0})
    },
    "Candelilla Wax": {
        "sap_koh": 0.044, "sap_naoh": 0.031, "iodine": 32, "ins": 12,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": {"hardness": 68, "cleansing": 0, "bubbly": 0, "creamy": 60, "conditioning": 60} # Exception ID 142
    },
    "Canola Oil": {
        "sap_koh": 0.186, "sap_naoh": 0.133, "iodine": 110, "ins": 56,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 2, "ricinoleic": 0, "oleic": 61, "linoleic": 21, "linolenic": 9},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 2, "ricinoleic": 0, "oleic": 61, "linoleic": 21, "linolenic": 9})
    },
    "Canola Oil, high oleic": {
        "sap_koh": 0.186, "sap_naoh": 0.133, "iodine": 96, "ins": 90,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 2, "ricinoleic": 0, "oleic": 74, "linoleic": 12, "linolenic": 4},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 2, "ricinoleic": 0, "oleic": 74, "linoleic": 12, "linolenic": 4})
    },
    "Carrot Seed Oil, cold pressed": {
        "sap_koh": 0.144, "sap_naoh": 0.103, "iodine": 56, "ins": 0,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 0, "ricinoleic": 0, "oleic": 80, "linoleic": 13, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 0, "ricinoleic": 0, "oleic": 80, "linoleic": 13, "linolenic": 0})
    },
    "Castor Oil": {
        "sap_koh": 0.180, "sap_naoh": 0.128, "iodine": 86, "ins": 95,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 90, "oleic": 4, "linoleic": 4, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 90, "oleic": 4, "linoleic": 4, "linolenic": 0})
    },
    "Cherry Kern1 Oil, p. avium": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 128, "ins": 62,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 31, "linoleic": 45, "linolenic": 11},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 31, "linoleic": 45, "linolenic": 11})
    },
    "Cherry Kern2 Oil, p. cerasus": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 118, "ins": 74,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 50, "linoleic": 40, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 50, "linoleic": 40, "linolenic": 0})
    },
    "Chicken Fat": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 69, "ins": 130,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 25, "stearic": 7, "ricinoleic": 0, "oleic": 38, "linoleic": 21, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 25, "stearic": 7, "ricinoleic": 0, "oleic": 38, "linoleic": 21, "linolenic": 0})
    },
    "Cocoa Butter": {
        "sap_koh": 0.194, "sap_naoh": 0.138, "iodine": 37, "ins": 157,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 28, "stearic": 33, "ricinoleic": 0, "oleic": 35, "linoleic": 3, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 28, "stearic": 33, "ricinoleic": 0, "oleic": 35, "linoleic": 3, "linolenic": 0})
    },
    "Coconut Oil, 76 deg": {
        "sap_koh": 0.257, "sap_naoh": 0.183, "iodine": 10, "ins": 258,
        "fa": {"lauric": 48, "myristic": 19, "palmitic": 9, "stearic": 3, "ricinoleic": 0, "oleic": 8, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 48, "myristic": 19, "palmitic": 9, "stearic": 3, "ricinoleic": 0, "oleic": 8, "linoleic": 2, "linolenic": 0})
    },
    "Coconut Oil, 92 deg": {
        "sap_koh": 0.257, "sap_naoh": 0.183, "iodine": 3, "ins": 258,
        "fa": {"lauric": 48, "myristic": 19, "palmitic": 9, "stearic": 3, "ricinoleic": 0, "oleic": 8, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 48, "myristic": 19, "palmitic": 9, "stearic": 3, "ricinoleic": 0, "oleic": 8, "linoleic": 2, "linolenic": 0})
    },
    "Coconut Oil, fractionated": {
        "sap_koh": 0.325, "sap_naoh": 0.232, "iodine": 1, "ins": 324,
        "fa": {"lauric": 2, "myristic": 1, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": {"hardness": 100, "cleansing": 100, "bubbly": 100, "creamy": 0, "conditioning": 0} # Exception ID 65
    },
    "Coffee Bean Oil, green": {
        "sap_koh": 0.185, "sap_naoh": 0.132, "iodine": 85, "ins": 100,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 38, "stearic": 8, "ricinoleic": 0, "oleic": 9, "linoleic": 39, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 38, "stearic": 8, "ricinoleic": 0, "oleic": 9, "linoleic": 39, "linolenic": 2})
    },
    "Coffee Bean Oil, roasted": {
        "sap_koh": 0.180, "sap_naoh": 0.128, "iodine": 87, "ins": 93,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 40, "stearic": 0, "ricinoleic": 0, "oleic": 8, "linoleic": 38, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 40, "stearic": 0, "ricinoleic": 0, "oleic": 8, "linoleic": 38, "linolenic": 2})
    },
    "Cohune Oil": {
        "sap_koh": 0.205, "sap_naoh": 0.146, "iodine": 30, "ins": 175,
        "fa": {"lauric": 51, "myristic": 13, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 18, "linoleic": 3, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 51, "myristic": 13, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 18, "linoleic": 3, "linolenic": 0})
    },
    "Corn Oil": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 117, "ins": 69,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 12, "stearic": 2, "ricinoleic": 0, "oleic": 32, "linoleic": 51, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 12, "stearic": 2, "ricinoleic": 0, "oleic": 32, "linoleic": 51, "linolenic": 1})
    },
    "Cottonseed Oil": {
        "sap_koh": 0.194, "sap_naoh": 0.138, "iodine": 108, "ins": 89,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 13, "ricinoleic": 0, "oleic": 18, "linoleic": 52, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 13, "ricinoleic": 0, "oleic": 18, "linoleic": 52, "linolenic": 1})
    },
    "Cranberry Seed Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 150, "ins": 40,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 23, "linoleic": 37, "linolenic": 32},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 23, "linoleic": 37, "linolenic": 32})
    },
    "Crisco, new w/palm": {
        "sap_koh": 0.193, "sap_naoh": 0.138, "iodine": 111, "ins": 82,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 20, "stearic": 5, "ricinoleic": 0, "oleic": 28, "linoleic": 40, "linolenic": 6},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 20, "stearic": 5, "ricinoleic": 0, "oleic": 28, "linoleic": 40, "linolenic": 6})
    },
    "Crisco, old": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 93, "ins": 115,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 13, "ricinoleic": 0, "oleic": 18, "linoleic": 52, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 13, "ricinoleic": 0, "oleic": 18, "linoleic": 52, "linolenic": 0})
    },
    "Cupuacu Butter": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 39, "ins": 153,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 35, "ricinoleic": 0, "oleic": 42, "linoleic": 2, "linolenic": 0},
        "qualities": {"hardness": 54, "cleansing": 0, "bubbly": 0, "creamy": 43, "conditioning": 44} # Exception ID 101
    },
    "Duck Fat, flesh and skin": {
        "sap_koh": 0.194, "sap_naoh": 0.138, "iodine": 72, "ins": 122,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 26, "stearic": 9, "ricinoleic": 0, "oleic": 44, "linoleic": 13, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 26, "stearic": 9, "ricinoleic": 0, "oleic": 44, "linoleic": 13, "linolenic": 1})
    },
    "Emu Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 60, "ins": 128,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 23, "stearic": 9, "ricinoleic": 0, "oleic": 47, "linoleic": 8, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 23, "stearic": 9, "ricinoleic": 0, "oleic": 47, "linoleic": 8, "linolenic": 0})
    },
    "Evening Primrose Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 160, "ins": 30,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 80, "linolenic": 9},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 80, "linolenic": 9})
    },
    "Flax Oil, linseed": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 180, "ins": -6,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 27, "linoleic": 13, "linolenic": 50},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 27, "linoleic": 13, "linolenic": 50})
    },
    "Ghee, any bovine": {
        "sap_koh": 0.227, "sap_naoh": 0.162, "iodine": 30, "ins": 191,
        "fa": {"lauric": 4, "myristic": 11, "palmitic": 28, "stearic": 12, "ricinoleic": 0, "oleic": 19, "linoleic": 2, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 4, "myristic": 11, "palmitic": 28, "stearic": 12, "ricinoleic": 0, "oleic": 19, "linoleic": 2, "linolenic": 1})
    },
    "Goose Fat": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 65, "ins": 130,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 21, "stearic": 6, "ricinoleic": 0, "oleic": 54, "linoleic": 10, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 21, "stearic": 6, "ricinoleic": 0, "oleic": 54, "linoleic": 10, "linolenic": 0})
    },
    "Grapeseed Oil": {
        "sap_koh": 0.181, "sap_naoh": 0.129, "iodine": 131, "ins": 66,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 4, "ricinoleic": 0, "oleic": 20, "linoleic": 68, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 4, "ricinoleic": 0, "oleic": 20, "linoleic": 68, "linolenic": 0})
    },
    "Hazelnut Oil": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 97, "ins": 94,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 5, "stearic": 3, "ricinoleic": 0, "oleic": 75, "linoleic": 10, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 5, "stearic": 3, "ricinoleic": 0, "oleic": 75, "linoleic": 10, "linolenic": 0})
    },
    "Hemp Oil": {
        "sap_koh": 0.193, "sap_naoh": 0.138, "iodine": 165, "ins": 39,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 12, "linoleic": 57, "linolenic": 21},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 12, "linoleic": 57, "linolenic": 21})
    },
    "Horse Oil": {
        "sap_koh": 0.196, "sap_naoh": 0.140, "iodine": 79, "ins": 117,
        "fa": {"lauric": 0, "myristic": 3, "palmitic": 26, "stearic": 5, "ricinoleic": 0, "oleic": 10, "linoleic": 20, "linolenic": 19},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 3, "palmitic": 26, "stearic": 5, "ricinoleic": 0, "oleic": 10, "linoleic": 20, "linolenic": 19})
    },
    "Illipe Butter": {
        "sap_koh": 0.185, "sap_naoh": 0.132, "iodine": 33, "ins": 152,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 17, "stearic": 45, "ricinoleic": 0, "oleic": 35, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 17, "stearic": 45, "ricinoleic": 0, "oleic": 35, "linoleic": 0, "linolenic": 0})
    },
    "Japan Wax": {
        "sap_koh": 0.215, "sap_naoh": 0.153, "iodine": 11, "ins": 204,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 80, "stearic": 7, "ricinoleic": 0, "oleic": 4, "linoleic": 0, "linolenic": 0},
        "qualities": {"hardness": 68, "cleansing": 0, "bubbly": 0, "creamy": 60, "conditioning": 60} # Exception ID 143
    },
    "Jatropha Oil, soapnut seed oil": {
        "sap_koh": 0.193, "sap_naoh": 0.138, "iodine": 102, "ins": 91,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 7, "ricinoleic": 0, "oleic": 44, "linoleic": 34, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 7, "ricinoleic": 0, "oleic": 44, "linoleic": 34, "linolenic": 0})
    },
    "Jojoba Oil (a Liquid Wax Ester)": {
        "sap_koh": 0.092, "sap_naoh": 0.066, "iodine": 83, "ins": 11,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 12, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 12, "linoleic": 0, "linolenic": 0})
    },
    "Karanja Oil": {
        "sap_koh": 0.183, "sap_naoh": 0.130, "iodine": 85, "ins": 98,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 6, "ricinoleic": 0, "oleic": 58, "linoleic": 15, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 6, "ricinoleic": 0, "oleic": 58, "linoleic": 15, "linolenic": 0})
    },
    "Kokum Butter": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 35, "ins": 155,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 56, "ricinoleic": 0, "oleic": 36, "linoleic": 1, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 56, "ricinoleic": 0, "oleic": 36, "linoleic": 1, "linolenic": 0})
    },
    "Kpangnan Butter": {
        "sap_koh": 0.191, "sap_naoh": 0.136, "iodine": 42, "ins": 149,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 44, "ricinoleic": 0, "oleic": 49, "linoleic": 1, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 44, "ricinoleic": 0, "oleic": 49, "linoleic": 1, "linolenic": 0})
    },
    "Kukui nut Oil": {
        "sap_koh": 0.189, "sap_naoh": 0.135, "iodine": 168, "ins": 24,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 20, "linoleic": 42, "linolenic": 29},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 20, "linoleic": 42, "linolenic": 29})
    },
    "Lanolin liquid Wax": {
        "sap_koh": 0.106, "sap_naoh": 0.076, "iodine": 27, "ins": 83,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Lard, Pig Tallow (Manteca)": {
        "sap_koh": 0.198, "sap_naoh": 0.141, "iodine": 57, "ins": 139,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 28, "stearic": 13, "ricinoleic": 0, "oleic": 46, "linoleic": 6, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 28, "stearic": 13, "ricinoleic": 0, "oleic": 46, "linoleic": 6, "linolenic": 0})
    },
    "Laurel Fruit Oil": {
        "sap_koh": 0.198, "sap_naoh": 0.141, "iodine": 74, "ins": 124,
        "fa": {"lauric": 25, "myristic": 1, "palmitic": 15, "stearic": 1, "ricinoleic": 0, "oleic": 31, "linoleic": 26, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 25, "myristic": 1, "palmitic": 15, "stearic": 1, "ricinoleic": 0, "oleic": 31, "linoleic": 26, "linolenic": 1})
    },
    "Lauric Acid": {
        "sap_koh": 0.280, "sap_naoh": 0.200, "iodine": 0, "ins": 280,
        "fa": {"lauric": 99, "myristic": 1, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 99, "myristic": 1, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Linseed Oil, flax": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 180, "ins": -6,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 27, "linoleic": 13, "linolenic": 50},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 27, "linoleic": 13, "linolenic": 50})
    },
    "Loofa Seed Oil, Luffa cylinderica": {
        "sap_koh": 0.187, "sap_naoh": 0.133, "iodine": 108, "ins": 79,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 18, "ricinoleic": 0, "oleic": 30, "linoleic": 47, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 18, "ricinoleic": 0, "oleic": 30, "linoleic": 47, "linolenic": 0})
    },
    "Macadamia Nut Butter": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 70, "ins": 118,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 6, "stearic": 12, "ricinoleic": 0, "oleic": 56, "linoleic": 3, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 6, "stearic": 12, "ricinoleic": 0, "oleic": 56, "linoleic": 3, "linolenic": 1})
    },
    "Macadamia Nut Oil": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 76, "ins": 119,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 5, "ricinoleic": 0, "oleic": 59, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 5, "ricinoleic": 0, "oleic": 59, "linoleic": 2, "linolenic": 0})
    },
    "Mafura Butter, Trichilia emetica ": {
        "sap_koh": 0.198, "sap_naoh": 0.141, "iodine": 66, "ins": 132,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 37, "stearic": 3, "ricinoleic": 0, "oleic": 49, "linoleic": 11, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 37, "stearic": 3, "ricinoleic": 0, "oleic": 49, "linoleic": 11, "linolenic": 1})
    },
    "Mango Seed Butter": {
        "sap_koh": 0.191, "sap_naoh": 0.136, "iodine": 45, "ins": 146,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 42, "ricinoleic": 0, "oleic": 45, "linoleic": 3, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 42, "ricinoleic": 0, "oleic": 45, "linoleic": 3, "linolenic": 0})
    },
    "Mango Seed Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 60, "ins": 130,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 27, "ricinoleic": 0, "oleic": 52, "linoleic": 8, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 27, "ricinoleic": 0, "oleic": 52, "linoleic": 8, "linolenic": 1})
    },
    "Marula Oil": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 73, "ins": 119,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 7, "ricinoleic": 0, "oleic": 75, "linoleic": 4, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 7, "ricinoleic": 0, "oleic": 75, "linoleic": 4, "linolenic": 0})
    },
    "Meadowfoam Oil": {
        "sap_koh": 0.169, "sap_naoh": 0.120, "iodine": 92, "ins": 77,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": {"hardness": 2, "cleansing": 0, "bubbly": 0, "creamy": 2, "conditioning": 98} # Exception ID 31
    },
    "Milk Fat, any bovine": {
        "sap_koh": 0.227, "sap_naoh": 0.162, "iodine": 30, "ins": 191,
        "fa": {"lauric": 4, "myristic": 11, "palmitic": 28, "stearic": 12, "ricinoleic": 0, "oleic": 19, "linoleic": 2, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 4, "myristic": 11, "palmitic": 28, "stearic": 12, "ricinoleic": 0, "oleic": 19, "linoleic": 2, "linolenic": 1})
    },
    "Milk Thistle Oil": {
        "sap_koh": 0.196, "sap_naoh": 0.140, "iodine": 115, "ins": 81,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 2, "ricinoleic": 0, "oleic": 26, "linoleic": 64, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 2, "ricinoleic": 0, "oleic": 26, "linoleic": 64, "linolenic": 0})
    },
    "Mink Oil": {
        "sap_koh": 0.196, "sap_naoh": 0.140, "iodine": 55, "ins": 141,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Monoi de Tahiti  Oil": {
        "sap_koh": 0.255, "sap_naoh": 0.182, "iodine": 9, "ins": 246,
        "fa": {"lauric": 44, "myristic": 16, "palmitic": 10, "stearic": 3, "ricinoleic": 0, "oleic": 0, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 44, "myristic": 16, "palmitic": 10, "stearic": 3, "ricinoleic": 0, "oleic": 0, "linoleic": 2, "linolenic": 0})
    },
    "Moringa Oil": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 68, "ins": 124,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 7, "ricinoleic": 0, "oleic": 71, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 7, "ricinoleic": 0, "oleic": 71, "linoleic": 2, "linolenic": 0})
    },
    "Mowrah Butter": {
        "sap_koh": 0.194, "sap_naoh": 0.138, "iodine": 62, "ins": 132,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 24, "stearic": 22, "ricinoleic": 0, "oleic": 36, "linoleic": 15, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 24, "stearic": 22, "ricinoleic": 0, "oleic": 36, "linoleic": 15, "linolenic": 0})
    },
    "Murumuru Butter": {
        "sap_koh": 0.275, "sap_naoh": 0.196, "iodine": 25, "ins": 250,
        "fa": {"lauric": 47, "myristic": 26, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 15, "linoleic": 3, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 47, "myristic": 26, "palmitic": 6, "stearic": 3, "ricinoleic": 0, "oleic": 15, "linoleic": 3, "linolenic": 0})
    },
    "Mustard Oil, kachi ghani": {
        "sap_koh": 0.173, "sap_naoh": 0.123, "iodine": 101, "ins": 72,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 2, "stearic": 2, "ricinoleic": 0, "oleic": 18, "linoleic": 14, "linolenic": 9},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 2, "stearic": 2, "ricinoleic": 0, "oleic": 18, "linoleic": 14, "linolenic": 9})
    },
    "Myristic Acid": {
        "sap_koh": 0.247, "sap_naoh": 0.176, "iodine": 1, "ins": 246,
        "fa": {"lauric": 0, "myristic": 99, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 99, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Neatsfoot Oil": {
        "sap_koh": 0.180, "sap_naoh": 0.128, "iodine": 90, "ins": 90,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Neem Seed Oil": {
        "sap_koh": 0.193, "sap_naoh": 0.138, "iodine": 72, "ins": 121,
        "fa": {"lauric": 0, "myristic": 2, "palmitic": 21, "stearic": 16, "ricinoleic": 0, "oleic": 46, "linoleic": 12, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 2, "palmitic": 21, "stearic": 16, "ricinoleic": 0, "oleic": 46, "linoleic": 12, "linolenic": 0})
    },
    "Nutmeg Butter": {
        "sap_koh": 0.162, "sap_naoh": 0.116, "iodine": 46, "ins": 116,
        "fa": {"lauric": 3, "myristic": 83, "palmitic": 4, "stearic": 0, "ricinoleic": 0, "oleic": 5, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 3, "myristic": 83, "palmitic": 4, "stearic": 0, "ricinoleic": 0, "oleic": 5, "linoleic": 0, "linolenic": 0})
    },
    "Oat Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 104, "ins": 86,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 15, "stearic": 2, "ricinoleic": 0, "oleic": 40, "linoleic": 39, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 15, "stearic": 2, "ricinoleic": 0, "oleic": 40, "linoleic": 39, "linolenic": 0})
    },
    "Oleic Acid": {
        "sap_koh": 0.202, "sap_naoh": 0.144, "iodine": 92, "ins": 110,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 99, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 99, "linoleic": 0, "linolenic": 0})
    },
    "Olive Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 85, "ins": 105,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 14, "stearic": 3, "ricinoleic": 0, "oleic": 69, "linoleic": 12, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 14, "stearic": 3, "ricinoleic": 0, "oleic": 69, "linoleic": 12, "linolenic": 1})
    },
    "Olive Oil  pomace": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 84, "ins": 104,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 14, "stearic": 3, "ricinoleic": 0, "oleic": 69, "linoleic": 12, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 14, "stearic": 3, "ricinoleic": 0, "oleic": 69, "linoleic": 12, "linolenic": 2})
    },
    "Ostrich Oil": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 97, "ins": 128,
        "fa": {"lauric": 3, "myristic": 1, "palmitic": 26, "stearic": 6, "ricinoleic": 0, "oleic": 37, "linoleic": 17, "linolenic": 3},
        "qualities": _calc_qualities({"lauric": 3, "myristic": 1, "palmitic": 26, "stearic": 6, "ricinoleic": 0, "oleic": 37, "linoleic": 17, "linolenic": 3})
    },
    "Palm Kernel Oil": {
        "sap_koh": 0.247, "sap_naoh": 0.176, "iodine": 20, "ins": 227,
        "fa": {"lauric": 49, "myristic": 16, "palmitic": 8, "stearic": 2, "ricinoleic": 0, "oleic": 15, "linoleic": 3, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 49, "myristic": 16, "palmitic": 8, "stearic": 2, "ricinoleic": 0, "oleic": 15, "linoleic": 3, "linolenic": 0})
    },
    "Palm Kernel Oil Flakes, hydrogenated": {
        "sap_koh": 0.247, "sap_naoh": 0.176, "iodine": 20, "ins": 227,
        "fa": {"lauric": 49, "myristic": 17, "palmitic": 8, "stearic": 16, "ricinoleic": 0, "oleic": 4, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 49, "myristic": 17, "palmitic": 8, "stearic": 16, "ricinoleic": 0, "oleic": 4, "linoleic": 0, "linolenic": 0})
    },
    "Palm Oil": {
        "sap_koh": 0.199, "sap_naoh": 0.142, "iodine": 53, "ins": 145,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 44, "stearic": 5, "ricinoleic": 0, "oleic": 39, "linoleic": 10, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 44, "stearic": 5, "ricinoleic": 0, "oleic": 39, "linoleic": 10, "linolenic": 0})
    },
    "Palm Stearin": {
        "sap_koh": 0.199, "sap_naoh": 0.142, "iodine": 48, "ins": 151,
        "fa": {"lauric": 0, "myristic": 2, "palmitic": 60, "stearic": 5, "ricinoleic": 0, "oleic": 26, "linoleic": 7, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 2, "palmitic": 60, "stearic": 5, "ricinoleic": 0, "oleic": 26, "linoleic": 7, "linolenic": 0})
    },
    "Palmitic Acid": {
        "sap_koh": 0.215, "sap_naoh": 0.153, "iodine": 2, "ins": 213,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 98, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 98, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Palmolein": {
        "sap_koh": 0.200, "sap_naoh": 0.143, "iodine": 58, "ins": 142,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 40, "stearic": 5, "ricinoleic": 0, "oleic": 43, "linoleic": 11, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 40, "stearic": 5, "ricinoleic": 0, "oleic": 43, "linoleic": 11, "linolenic": 0})
    },
    "Papaya seed oil, Carica papaya": {
        "sap_koh": 0.158, "sap_naoh": 0.113, "iodine": 67, "ins": 91,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 5, "ricinoleic": 0, "oleic": 76, "linoleic": 3, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 5, "ricinoleic": 0, "oleic": 76, "linoleic": 3, "linolenic": 0})
    },
    "Passion Fruit Seed Oil": {
        "sap_koh": 0.183, "sap_naoh": 0.130, "iodine": 136, "ins": 47,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 3, "ricinoleic": 0, "oleic": 15, "linoleic": 70, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 3, "ricinoleic": 0, "oleic": 15, "linoleic": 70, "linolenic": 1})
    },
    "Pataua (Patawa) Oil": {
        "sap_koh": 0.200, "sap_naoh": 0.143, "iodine": 77, "ins": 123,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 4, "ricinoleic": 0, "oleic": 78, "linoleic": 3, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 13, "stearic": 4, "ricinoleic": 0, "oleic": 78, "linoleic": 3, "linolenic": 1})
    },
    "Peach Kernel Oil": {
        "sap_koh": 0.191, "sap_naoh": 0.136, "iodine": 108, "ins": 87,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 65, "linoleic": 25, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 65, "linoleic": 25, "linolenic": 1})
    },
    "Peanut Oil": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 92, "ins": 99,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 56, "linoleic": 26, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 8, "stearic": 3, "ricinoleic": 0, "oleic": 56, "linoleic": 26, "linolenic": 0})
    },
    "Pecan Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 113, "ins": 77,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 2, "ricinoleic": 0, "oleic": 50, "linoleic": 39, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 2, "ricinoleic": 0, "oleic": 50, "linoleic": 39, "linolenic": 2})
    },
    "Perilla Seed Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 196, "ins": -6,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 15, "linoleic": 16, "linolenic": 56},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 2, "ricinoleic": 0, "oleic": 15, "linoleic": 16, "linolenic": 56})
    },
    "Pine Tar, lye calc only no FA": {
        "sap_koh": 0.060, "sap_naoh": 0.043, "iodine": 0, "ins": 0,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 0, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Pistachio Oil": {
        "sap_koh": 0.186, "sap_naoh": 0.133, "iodine": 95, "ins": 92,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 1, "ricinoleic": 0, "oleic": 63, "linoleic": 25, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 1, "ricinoleic": 0, "oleic": 63, "linoleic": 25, "linolenic": 0})
    },
    "Plum Kernel Oil": {
        "sap_koh": 0.194, "sap_naoh": 0.138, "iodine": 98, "ins": 96,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 0, "ricinoleic": 0, "oleic": 68, "linoleic": 23, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 0, "ricinoleic": 0, "oleic": 68, "linoleic": 23, "linolenic": 0})
    },
    "Pomegranate Seed Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 22, "ins": 168,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 3, "ricinoleic": 0, "oleic": 7, "linoleic": 7, "linolenic": 78},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 3, "ricinoleic": 0, "oleic": 7, "linoleic": 7, "linolenic": 78})
    },
    "Poppy Seed Oil": {
        "sap_koh": 0.194, "sap_naoh": 0.138, "iodine": 140, "ins": 54,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 2, "ricinoleic": 0, "oleic": 17, "linoleic": 69, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 2, "ricinoleic": 0, "oleic": 17, "linoleic": 69, "linolenic": 2})
    },
    "Pracaxi (Pracachy) Seed Oil - hair conditioner": {
        "sap_koh": 0.175, "sap_naoh": 0.125, "iodine": 68, "ins": 107,
        "fa": {"lauric": 1, "myristic": 1, "palmitic": 2, "stearic": 2, "ricinoleic": 0, "oleic": 44, "linoleic": 2, "linolenic": 2},
        "qualities": {"hardness": 6, "cleansing": 2, "bubbly": 2, "creamy": 4, "conditioning": 83} # Exception ID 149
    },
    "Pumpkin Seed Oil virgin": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 128, "ins": 67,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 8, "ricinoleic": 0, "oleic": 33, "linoleic": 50, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 8, "ricinoleic": 0, "oleic": 33, "linoleic": 50, "linolenic": 0})
    },
    "Rabbit Fat": {
        "sap_koh": 0.201, "sap_naoh": 0.143, "iodine": 85, "ins": 116,
        "fa": {"lauric": 0, "myristic": 3, "palmitic": 30, "stearic": 6, "ricinoleic": 0, "oleic": 30, "linoleic": 20, "linolenic": 5},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 3, "palmitic": 30, "stearic": 6, "ricinoleic": 0, "oleic": 30, "linoleic": 20, "linolenic": 5})
    },
    "Rapeseed Oil, unrefined canola": {
        "sap_koh": 0.175, "sap_naoh": 0.125, "iodine": 106, "ins": 69,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 1, "ricinoleic": 0, "oleic": 17, "linoleic": 13, "linolenic": 9},
        "qualities": {"hardness": 5, "cleansing": 0, "bubbly": 0, "creamy": 1, "conditioning": 95} # Exception ID 40
    },
    "Raspberry Seed Oil": {
        "sap_koh": 0.187, "sap_naoh": 0.133, "iodine": 163, "ins": 24,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 0, "ricinoleic": 0, "oleic": 13, "linoleic": 55, "linolenic": 26},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 0, "ricinoleic": 0, "oleic": 13, "linoleic": 55, "linolenic": 26})
    },
    "Red Palm Butter": {
        "sap_koh": 0.199, "sap_naoh": 0.142, "iodine": 53, "ins": 145,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 44, "stearic": 5, "ricinoleic": 0, "oleic": 39, "linoleic": 10, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 44, "stearic": 5, "ricinoleic": 0, "oleic": 39, "linoleic": 10, "linolenic": 0})
    },
    "Rice Bran Oil, refined": {
        "sap_koh": 0.187, "sap_naoh": 0.133, "iodine": 100, "ins": 87,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 22, "stearic": 3, "ricinoleic": 0, "oleic": 38, "linoleic": 34, "linolenic": 2},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 22, "stearic": 3, "ricinoleic": 0, "oleic": 38, "linoleic": 34, "linolenic": 2})
    },
    "Rosehip Oil": {
        "sap_koh": 0.187, "sap_naoh": 0.133, "iodine": 188, "ins": 10,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 2, "ricinoleic": 0, "oleic": 12, "linoleic": 46, "linolenic": 31},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 2, "ricinoleic": 0, "oleic": 12, "linoleic": 46, "linolenic": 31})
    },
    "Sacha Inchi, Plukenetia volubilis": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 141, "ins": 47,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 3, "ricinoleic": 0, "oleic": 10, "linoleic": 35, "linolenic": 48},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 4, "stearic": 3, "ricinoleic": 0, "oleic": 10, "linoleic": 35, "linolenic": 48})
    },
    "Safflower Oil": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 145, "ins": 47,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 0, "ricinoleic": 0, "oleic": 15, "linoleic": 75, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 0, "ricinoleic": 0, "oleic": 15, "linoleic": 75, "linolenic": 0})
    },
    "Safflower Oil, high oleic": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 93, "ins": 97,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 5, "stearic": 2, "ricinoleic": 0, "oleic": 77, "linoleic": 15, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 5, "stearic": 2, "ricinoleic": 0, "oleic": 77, "linoleic": 15, "linolenic": 0})
    },
    "Sal Butter": {
        "sap_koh": 0.185, "sap_naoh": 0.132, "iodine": 39, "ins": 146,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 44, "ricinoleic": 0, "oleic": 40, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 44, "ricinoleic": 0, "oleic": 40, "linoleic": 2, "linolenic": 0})
    },
    "Salmon Oil": {
        "sap_koh": 0.185, "sap_naoh": 0.132, "iodine": 169, "ins": 16,
        "fa": {"lauric": 0, "myristic": 5, "palmitic": 19, "stearic": 2, "ricinoleic": 0, "oleic": 23, "linoleic": 2, "linolenic": 1},
        "qualities": {"hardness": 28, "cleansing": 0, "bubbly": 0, "creamy": 3, "conditioning": 72} # Exception ID 140
    },
    "Saw Palmetto Extract": {
        "sap_koh": 0.230, "sap_naoh": 0.164, "iodine": 45, "ins": 185,
        "fa": {"lauric": 29, "myristic": 11, "palmitic": 8, "stearic": 2, "ricinoleic": 0, "oleic": 35, "linoleic": 4, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 29, "myristic": 11, "palmitic": 8, "stearic": 2, "ricinoleic": 0, "oleic": 35, "linoleic": 4, "linolenic": 1})
    },
    "Saw Palmetto Oil": {
        "sap_koh": 0.220, "sap_naoh": 0.157, "iodine": 44, "ins": 176,
        "fa": {"lauric": 29, "myristic": 13, "palmitic": 9, "stearic": 2, "ricinoleic": 0, "oleic": 31, "linoleic": 4, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 29, "myristic": 13, "palmitic": 9, "stearic": 2, "ricinoleic": 0, "oleic": 31, "linoleic": 4, "linolenic": 1})
    },
    "Sea Buckthorn Oil, seed": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 165, "ins": 30,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 3, "ricinoleic": 0, "oleic": 14, "linoleic": 36, "linolenic": 38},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 3, "ricinoleic": 0, "oleic": 14, "linoleic": 36, "linolenic": 38})
    },
    "Sea Buckthorn Oil, seed and berry": {
        "sap_koh": 0.183, "sap_naoh": 0.130, "iodine": 86, "ins": 97,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 30, "stearic": 1, "ricinoleic": 0, "oleic": 28, "linoleic": 10, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 30, "stearic": 1, "ricinoleic": 0, "oleic": 28, "linoleic": 10, "linolenic": 0})
    },
    "Sesame Oil": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 110, "ins": 81,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 5, "ricinoleic": 0, "oleic": 40, "linoleic": 43, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 10, "stearic": 5, "ricinoleic": 0, "oleic": 40, "linoleic": 43, "linolenic": 0})
    },
    "Shea Butter": {
        "sap_koh": 0.179, "sap_naoh": 0.128, "iodine": 59, "ins": 116,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 5, "stearic": 40, "ricinoleic": 0, "oleic": 48, "linoleic": 6, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 5, "stearic": 40, "ricinoleic": 0, "oleic": 48, "linoleic": 6, "linolenic": 0})
    },
    "Shea Oil, fractionated": {
        "sap_koh": 0.185, "sap_naoh": 0.132, "iodine": 83, "ins": 102,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 10, "ricinoleic": 0, "oleic": 73, "linoleic": 11, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 6, "stearic": 10, "ricinoleic": 0, "oleic": 73, "linoleic": 11, "linolenic": 0})
    },
    "SoapQuick, conventional": {
        "sap_koh": 0.212, "sap_naoh": 0.151, "iodine": 59, "ins": 153,
        "fa": {"lauric": 13, "myristic": 6, "palmitic": 17, "stearic": 3, "ricinoleic": 5, "oleic": 42, "linoleic": 8, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 13, "myristic": 6, "palmitic": 17, "stearic": 3, "ricinoleic": 5, "oleic": 42, "linoleic": 8, "linolenic": 1})
    },
    "SoapQuick, organic": {
        "sap_koh": 0.213, "sap_naoh": 0.152, "iodine": 56, "ins": 156,
        "fa": {"lauric": 13, "myristic": 5, "palmitic": 20, "stearic": 3, "ricinoleic": 0, "oleic": 45, "linoleic": 10, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 13, "myristic": 5, "palmitic": 20, "stearic": 3, "ricinoleic": 0, "oleic": 45, "linoleic": 10, "linolenic": 0})
    },
    "Soybean Oil": {
        "sap_koh": 0.191, "sap_naoh": 0.136, "iodine": 131, "ins": 61,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 5, "ricinoleic": 0, "oleic": 24, "linoleic": 50, "linolenic": 8},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 5, "ricinoleic": 0, "oleic": 24, "linoleic": 50, "linolenic": 8})
    },
    "Soybean, 27.5% hydrogenated": {
        "sap_koh": 0.191, "sap_naoh": 0.136, "iodine": 78, "ins": 113,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 15, "ricinoleic": 0, "oleic": 41, "linoleic": 7, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 15, "ricinoleic": 0, "oleic": 41, "linoleic": 7, "linolenic": 1})
    },
    "Soybean, fully hydrogenated (soy wax)": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 1, "ins": 191,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 87, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 87, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Stearic Acid": {
        "sap_koh": 0.198, "sap_naoh": 0.141, "iodine": 2, "ins": 196,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 99, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 99, "ricinoleic": 0, "oleic": 0, "linoleic": 0, "linolenic": 0})
    },
    "Sunflower Oil": {
        "sap_koh": 0.189, "sap_naoh": 0.135, "iodine": 133, "ins": 63,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 4, "ricinoleic": 0, "oleic": 16, "linoleic": 70, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 4, "ricinoleic": 0, "oleic": 16, "linoleic": 70, "linolenic": 1})
    },
    "Sunflower Oil, high oleic": {
        "sap_koh": 0.189, "sap_naoh": 0.135, "iodine": 83, "ins": 106,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 4, "ricinoleic": 0, "oleic": 83, "linoleic": 4, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 3, "stearic": 4, "ricinoleic": 0, "oleic": 83, "linoleic": 4, "linolenic": 1})
    },
    "Tallow Bear": {
        "sap_koh": 0.195, "sap_naoh": 0.139, "iodine": 92, "ins": 100,
        "fa": {"lauric": 0, "myristic": 2, "palmitic": 7, "stearic": 3, "ricinoleic": 0, "oleic": 70, "linoleic": 9, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 2, "palmitic": 7, "stearic": 3, "ricinoleic": 0, "oleic": 70, "linoleic": 9, "linolenic": 0})
    },
    "Tallow Beef": {
        "sap_koh": 0.200, "sap_naoh": 0.143, "iodine": 45, "ins": 147,
        "fa": {"lauric": 2, "myristic": 6, "palmitic": 28, "stearic": 22, "ricinoleic": 0, "oleic": 36, "linoleic": 3, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 2, "myristic": 6, "palmitic": 28, "stearic": 22, "ricinoleic": 0, "oleic": 36, "linoleic": 3, "linolenic": 1})
    },
    "Tallow Deer": {
        "sap_koh": 0.193, "sap_naoh": 0.138, "iodine": 31, "ins": 166,
        "fa": {"lauric": 0, "myristic": 1, "palmitic": 20, "stearic": 24, "ricinoleic": 0, "oleic": 30, "linoleic": 15, "linolenic": 3},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 1, "palmitic": 20, "stearic": 24, "ricinoleic": 0, "oleic": 30, "linoleic": 15, "linolenic": 3})
    },
    "Tallow Goat": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 40, "ins": 152,
        "fa": {"lauric": 5, "myristic": 11, "palmitic": 23, "stearic": 30, "ricinoleic": 0, "oleic": 29, "linoleic": 2, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 5, "myristic": 11, "palmitic": 23, "stearic": 30, "ricinoleic": 0, "oleic": 29, "linoleic": 2, "linolenic": 0})
    },
    "Tallow Sheep": {
        "sap_koh": 0.194, "sap_naoh": 0.138, "iodine": 54, "ins": 156,
        "fa": {"lauric": 4, "myristic": 10, "palmitic": 24, "stearic": 13, "ricinoleic": 0, "oleic": 26, "linoleic": 5, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 4, "myristic": 10, "palmitic": 24, "stearic": 13, "ricinoleic": 0, "oleic": 26, "linoleic": 5, "linolenic": 0})
    },
    "Tamanu Oil, kamani": {
        "sap_koh": 0.208, "sap_naoh": 0.148, "iodine": 111, "ins": 82,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 12, "stearic": 13, "ricinoleic": 0, "oleic": 34, "linoleic": 38, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 12, "stearic": 13, "ricinoleic": 0, "oleic": 34, "linoleic": 38, "linolenic": 1})
    },
    "Tucuma Seed Butter": {
        "sap_koh": 0.238, "sap_naoh": 0.170, "iodine": 13, "ins": 175,
        "fa": {"lauric": 48, "myristic": 23, "palmitic": 6, "stearic": 0, "ricinoleic": 0, "oleic": 13, "linoleic": 0, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 48, "myristic": 23, "palmitic": 6, "stearic": 0, "ricinoleic": 0, "oleic": 13, "linoleic": 0, "linolenic": 0})
    },
    "Ucuuba Butter": {
        "sap_koh": 0.205, "sap_naoh": 0.146, "iodine": 38, "ins": 167,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 31, "ricinoleic": 0, "oleic": 44, "linoleic": 5, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 0, "stearic": 31, "ricinoleic": 0, "oleic": 44, "linoleic": 5, "linolenic": 0})
    },
    "Walmart GV Shortening, tallow, palm": {
        "sap_koh": 0.198, "sap_naoh": 0.141, "iodine": 49, "ins": 151,
        "fa": {"lauric": 1, "myristic": 4, "palmitic": 35, "stearic": 14, "ricinoleic": 0, "oleic": 37, "linoleic": 6, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 1, "myristic": 4, "palmitic": 35, "stearic": 14, "ricinoleic": 0, "oleic": 37, "linoleic": 6, "linolenic": 1})
    },
    "Walnut Oil": {
        "sap_koh": 0.189, "sap_naoh": 0.135, "iodine": 145, "ins": 45,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 2, "ricinoleic": 0, "oleic": 18, "linoleic": 60, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 7, "stearic": 2, "ricinoleic": 0, "oleic": 18, "linoleic": 60, "linolenic": 0})
    },
    "Watermelon Seed Oil": {
        "sap_koh": 0.190, "sap_naoh": 0.135, "iodine": 119, "ins": 71,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 10, "ricinoleic": 0, "oleic": 18, "linoleic": 60, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 11, "stearic": 10, "ricinoleic": 0, "oleic": 18, "linoleic": 60, "linolenic": 1})
    },
    "Wheat Germ Oil": {
        "sap_koh": 0.183, "sap_naoh": 0.131, "iodine": 128, "ins": 58,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 17, "stearic": 2, "ricinoleic": 0, "oleic": 17, "linoleic": 58, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 17, "stearic": 2, "ricinoleic": 0, "oleic": 17, "linoleic": 58, "linolenic": 0})
    },
    "Yangu, cape chestnut": {
        "sap_koh": 0.192, "sap_naoh": 0.137, "iodine": 95, "ins": 97,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 18, "stearic": 5, "ricinoleic": 0, "oleic": 45, "linoleic": 30, "linolenic": 1},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 18, "stearic": 5, "ricinoleic": 0, "oleic": 45, "linoleic": 30, "linolenic": 1})
    },
    "Zapote seed oil, (Aceite de Sapuyul or Mamey)": {
        "sap_koh": 0.188, "sap_naoh": 0.134, "iodine": 72, "ins": 116,
        "fa": {"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 21, "ricinoleic": 0, "oleic": 52, "linoleic": 13, "linolenic": 0},
        "qualities": _calc_qualities({"lauric": 0, "myristic": 0, "palmitic": 9, "stearic": 21, "ricinoleic": 0, "oleic": 52, "linoleic": 13, "linolenic": 0})
    }
}

CUSTOM_OILS_FILE = "custom_oils.json"

def load_custom_oils():
    """Load custom oils from JSON file."""
    if os.path.exists(CUSTOM_OILS_FILE):
        try:
            with open(CUSTOM_OILS_FILE, 'r') as f:
                custom_oils = json.load(f)
                OILS.update(custom_oils)
        except Exception as e:
            print(f"Error loading custom oils: {e}")

def save_custom_oil(name: str, data: dict):
    """Save a custom oil to JSON and update memory."""
    # Update in-memory
    OILS[name] = data
    
    # Load existing custom oils to append/update
    custom_oils = {}
    if os.path.exists(CUSTOM_OILS_FILE):
        try:
            with open(CUSTOM_OILS_FILE, 'r') as f:
                custom_oils = json.load(f)
        except Exception:
            pass
    
    custom_oils[name] = data
    
    try:
        with open(CUSTOM_OILS_FILE, 'w') as f:
            json.dump(custom_oils, f, indent=4)
    except Exception as e:
        print(f"Error saving custom oil: {e}")

def delete_custom_oil(name: str):
    """Delete a custom oil."""
    if name in OILS:
        del OILS[name]
        
    custom_oils = {}
    if os.path.exists(CUSTOM_OILS_FILE):
        try:
            with open(CUSTOM_OILS_FILE, 'r') as f:
                custom_oils = json.load(f)
        except Exception:
            pass
            
    if name in custom_oils:
        del custom_oils[name]
        try:
            with open(CUSTOM_OILS_FILE, 'w') as f:
                json.dump(custom_oils, f, indent=4)
        except Exception as e:
            print(f"Error deleting custom oil: {e}")

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

class SoapMath:
    """
    Implements the exact calculation logic from SoapCalc.
    """
    
    @staticmethod
    def calculate_lye(oils: dict, lye_type: str = "NaOH", koh_purity: float = 1.0) -> float:
        """
        Calculate required lye mass.
        oils: dict of {oil_name: weight_in_grams}
        lye_type: "NaOH" or "KOH"
        koh_purity: 0.90 for 90% KOH, 1.0 for pure.
        """
        total_lye = 0.0
        for name, weight in oils.items():
            sap = get_oil_sap(name, lye_type)
            total_lye += weight * sap
            
        if lye_type == "KOH" and koh_purity < 1.0:
            total_lye = total_lye / koh_purity
            
        return total_lye

    @staticmethod
    def calculate_water(total_oil_weight: float, lye_mass: float, 
                       method: str = "percent_of_oils", value: float = 38.0) -> float:
        """
        Calculate water amount based on method.
        method: "percent_of_oils", "lye_concentration", "water_lye_ratio"
        """
        if method == "percent_of_oils":
            return total_oil_weight * (value / 100.0)
        elif method == "lye_concentration":
            # Concentration = Lye / (Lye + Water)
            # Water = (Lye / Concentration) - Lye
            if value <= 0: return 0.0
            return (lye_mass / (value / 100.0)) - lye_mass
        elif method == "water_lye_ratio":
            # Ratio = Water : Lye (e.g. 2:1 means value is 2.0)
            return lye_mass * value
        return 0.0

    @staticmethod
    def calculate_qualities(oils: dict) -> dict:
        """
        Calculate the final soap qualities (Hardness, Cleansing, etc.)
        Returns a dict with values scaled to the total batch weight.
        """
        total_weight = sum(oils.values())
        if total_weight == 0:
            return {}
            
        final_qualities = {
            "hardness": 0.0, "cleansing": 0.0, "bubbly": 0.0, 
            "creamy": 0.0, "conditioning": 0.0, "iodine": 0.0, "ins": 0.0
        }
        
        for name, weight in oils.items():
            oil_data = OILS.get(name)
            if not oil_data: continue
            
            ratio = weight / total_weight
            
            # Use pre-calculated qualities if available (exceptions), otherwise calculate from FA
            q = oil_data.get("qualities")
            if not q:
                q = _calc_qualities(oil_data.get("fa", {}))
            
            final_qualities["hardness"] += q.get("hardness", 0) * ratio
            final_qualities["cleansing"] += q.get("cleansing", 0) * ratio
            final_qualities["bubbly"] += q.get("bubbly", 0) * ratio
            final_qualities["creamy"] += q.get("creamy", 0) * ratio
            final_qualities["conditioning"] += q.get("conditioning", 0) * ratio
            
            final_qualities["iodine"] += oil_data.get("iodine", 0) * ratio
            final_qualities["ins"] += oil_data.get("ins", 0) * ratio
            
        return final_qualities

# Load custom oils on module import
load_custom_oils()
