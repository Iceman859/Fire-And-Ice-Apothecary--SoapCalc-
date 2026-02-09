"""Utility functions"""

import json
from pathlib import Path


def ensure_dir(directory: str) -> Path:
    """Ensure directory exists"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_number(value: float, decimals: int = 2) -> str:
    """Format number to string with specified decimal places"""
    return f"{value:.{decimals}f}"


def parse_number(value: str) -> float:
    """Parse string to float, return 0 if invalid"""
    try:
        return float(value)
    except ValueError:
        return 0.0
