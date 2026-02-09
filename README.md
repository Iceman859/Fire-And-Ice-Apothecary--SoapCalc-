# Fire and Ice Apothecary - SoapCalc

A comprehensive Python GUI application for soap making calculations and recipe management, replicating the functionality of SoapCalc.

## Overview

This application provides soap makers with professional-grade tools to:
- Calculate lye and water requirements for soap recipes
- Manage an extensive oil database with saponification values
- Support multiple lye types (NaOH and KOH)
- Create, save, and load soap recipes
- Scale recipes for different batch sizes
- Calculate batch costs and properties

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python main.py
```

## Features

### Core Calculations
- **Lye Calculation**: Automatically calculates sodium hydroxide (NaOH) and potassium hydroxide (KOH) requirements
- **Water Calculation**: Computes water amounts based on lye weight, water-to-lye ratio, and other factors
- **Oil Support**: Database of common soap-making oils with accurate SAP values
- **Batch Scaling**: Scale recipes up or down while maintaining proper ratios

### Recipe Management
- **Create Recipes**: Build custom soap recipes with multiple oils
- **Save/Load**: Save recipes as JSON files for future use
- **Edit**: Modify existing recipes and recalculate instantly
- **Import/Export**: Share recipes with other soap makers

### Advanced Features
- **Superfat Percentage**: Adjust unsaponified oil content
- **Water Ratios**: Fine-tune water-to-lye ratios for different soap types
- **Multiple Lye Types**: Calculate for both NaOH (cold process) and KOH (liquid soaps)
- **Batch Properties**: Display trace time estimates and hardness values

## Project Structure

```
src/
├── ui/              # PyQt6 GUI components
├── models/          # Calculation and data models
├── data/            # Oil database and constants
└── utils/           # Helper functions

recipes/            # Saved user recipes (JSON format)
tests/              # Unit tests
```

## Usage

1. **Select Oils**: Choose oils from the database and specify quantities
2. **Configure Settings**: Set lye type, water ratios, and superfat percentage
3. **View Calculations**: See lye and water requirements instantly
4. **Save Recipe**: Store recipes for future use
5. **Scale Batch**: Adjust total batch weight to increase/decrease recipe

## Contributing

Feel free to extend functionality, add more oils to the database, or improve the UI.

## License

Open source - feel free to modify and distribute as needed.
