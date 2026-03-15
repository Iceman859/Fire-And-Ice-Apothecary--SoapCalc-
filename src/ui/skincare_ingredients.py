"""
Default ingredient data for skincare making.
"""

EXFOLIANTS = {
    "Sugar": {},
    "Salt": {},
    "Coffee Grounds": {},
    "Pumice": {},
    "Walnut Shell Powder": {},
    "Jojoba Beads": {},
    "Oatmeal (Colloidal)": {},
}


def get_all_exfoliant_names():
    """Returns a sorted list of all exfoliant names."""
    return sorted(EXFOLIANTS.keys())


def is_exfoliant(name: str) -> bool:
    """Check if an ingredient name is a known exfoliant (case-insensitive)."""
    return name.lower() in [k.lower() for k in EXFOLIANTS.keys()]
