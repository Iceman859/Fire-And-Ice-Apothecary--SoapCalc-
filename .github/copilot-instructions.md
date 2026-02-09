# SoapCalc Python GUI Application

A Python-based GUI application that replicates the functionality of SoapCalc, a soap making calculator. This application provides comprehensive tools for soap makers to calculate lye quantities, water amounts, and manage soap recipes.

## Project Overview

- **Language**: Python 3.8+
- **Framework**: PyQt6 (GUI)
- **Purpose**: Soap making recipe calculator with recipe management

## Key Features

- Basic lye (NaOH/KOH) and water calculations
- Oil database with SAP (saponification) values
- Multiple lye type support
- Recipe management and scaling
- Save/load recipe functionality from JSON files

## Project Structure

```
Fire And Ice Apothecary (SoapCalc)/
├── src/
│   ├── ui/                 # PyQt6 GUI components
│   ├── models/             # Data models for calculations
│   ├── data/               # Oil database and default data
│   └── utils/              # Helper functions and utilities
├── recipes/                # Saved recipe files (JSON)
├── tests/                  # Unit tests
├── main.py                 # Application entry point
└── requirements.txt        # Python dependencies
```

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python main.py`

## Development Notes

- Oil database is loaded from JSON files in `src/data/`
- User recipes are saved to the `recipes/` directory
- All calculations follow cold process soap making standards
