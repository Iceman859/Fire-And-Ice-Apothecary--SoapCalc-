# Fire and Ice Apothecary - SoapCalc

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-Open%20Source-green)
![Status](https://img.shields.io/badge/Status-Active-success)

A comprehensive Python GUI application for soap making calculations and recipe management. Designed to provide professional-grade tools for modern soap makers, extending the classic functionality of SoapCalc with a modern interface and advanced features.

## 🚀 Overview

**Fire and Ice Apothecary - SoapCalc** empowers soap makers to formulate, calculate, and manage soap recipes with precision.

- **Calculate** lye and water requirements instantly.
- **Manage** a custom database of oils and additives.
- **Scale** recipes for any batch size or mold.
- **Analyze** costs and soap qualities (hardness, cleansing, conditioning).

## ✨ Features

### Core Calculations
- **Precision Lye Calculator**: Supports Sodium Hydroxide (NaOH) for bar soap, Potassium Hydroxide (KOH) for liquid soap, and dual-lye recipes.
- **Water Management**: Calculate water based on lye weight, water-to-lye ratio, or lye concentration.
- **Batch Scaling**: Resize recipes up or down while maintaining exact oil ratios.
- **Soap Qualities**: Real-time estimation of soap properties:
  - Hardness, Cleansing, Conditioning, Bubbly, Creamy, Iodine, INS.

### Recipe Management
- **Save & Load**: Store recipes as JSON files for easy sharing and backup.
- **Cost Calculation**: Estimate total batch cost and cost-per-bar based on ingredient prices.
- **Trace Estimates**: Predict trace times based on oil composition.
- **Import/Export**: Share recipes with the community.

### 🆕 Recent Updates
*([Edit this section with your latest features])*
- **UI Overhaul**: Updated PyQt6 interface for better usability.
- **Performance**: Faster calculation engine.
- *(Add your new features here, e.g., Fragrance Calculator, Inventory Tracking)*

## 🛠️ Installation

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1.  Clone or download this repository.
2.  Navigate to the project directory.
3.  Create and activate a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```
4.  Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running the Application

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
