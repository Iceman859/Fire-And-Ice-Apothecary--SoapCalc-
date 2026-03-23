"""UI REPORT TAB - Generate printable recipe reports and labels"""

from datetime import datetime

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
)
from src.models import SoapCalculator

try:
    from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

    _HAS_PRINTER = True
except ImportError:
    _HAS_PRINTER = False


class RecipeReportWidget(QWidget):
    """Widget for viewing and printing the recipe"""

    def __init__(self, view, calculator: SoapCalculator):
        super().__init__()
        self.view = view
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Toolbar
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh View")
        refresh_btn.clicked.connect(lambda: self.refresh_report())
        btn_layout.addWidget(refresh_btn)

        if _HAS_PRINTER:
            print_btn = QPushButton("Print / Save PDF")
            print_btn.clicked.connect(self.print_report)
            btn_layout.addWidget(print_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Viewer
        self.viewer = QTextBrowser()

        layout.addWidget(self.viewer)

        self.setLayout(layout)

    def refresh_report(self, recipe_name=None, notes=None):
        """Generate HTML report"""
        props = self.calculator.get_batch_properties()
        unit = self.calculator.unit_system
        unit_abbr = self.calculator.get_unit_abbreviation()
        qualities = props.get("relative_qualities", {})
        fa_profile = props.get("fa_breakdown", {})

        label_html = self.generate_label_html(props)

        # If no name is passed in, try to get it from the calculator
        if hasattr(self.view, 'current_recipe'):
            recipe_name = getattr(self.view.current_recipe, 'name', 'Untitled Recipe')

        # If no notes are passed in, try to get them from the calculator
        if not notes:
            notes = getattr(self.calculator, 'notes', '')

        # Define ranges for qualities
        quality_ranges = [
            ("Hardness", 29, 54),
            ("Cleansing", 12, 22),
            ("Conditioning", 44, 69),
            ("Bubbly", 14, 46),
            ("Creamy", 16, 48),
            ("Iodine", 41, 70),
            ("INS", 136, 165),
        ]

        # Helper to format weight
        def fmt(w):
            return f"{self.calculator.convert_weight(w, unit):.2f}"

        # Get Company Info
        settings = QSettings("FireAndIceApothecary", "SoapCalc")
        company_name = settings.value("company_name", "")
        website = settings.value("company_website", "")

        # Date
        date_str = datetime.now().strftime("%Y-%m-%d")

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; background-color: #fff; font-size: 11px; }}

                /* Letterhead Styles */
                .header-table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; border-bottom: 2px solid #1565c0; padding-bottom: 10px; }}
                .company-name {{ font-size: 22px; font-weight: bold; color: #1565c0; margin: 0; }}
                .company-web {{ font-size: 12px; color: #666; margin-top: 4px; }}
                .report-title {{ font-size: 18px; font-weight: bold; color: #333; text-align: right; }}
                .report-date {{ font-size: 11px; color: #888; text-align: right; margin-top: 4px; }}

                .section-header {{
                    background-color: #e3f2fd;
                    color: #0d47a1;
                    padding: 4px 8px;
                    font-weight: bold;
                    font-size: 1.0em;
                    margin-top: 10px;
                    border-left: 4px solid #1565c0;
                }}

                table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
                th {{ text-align: right; background-color: #f5f5f5; padding: 4px; border: 1px solid #e0e0e0; color: #424242; font-weight: bold; }}
                th.left-align {{ text-align: left; }}
                td {{ padding: 4px; border: 1px solid #f0f0f0; text-align: right; }}
                td.left-align {{ text-align: left; }}

                .param-table td {{ border: none; text-align: left; padding: 2px; }}
                .param-label {{ font-weight: bold; width: 160px; }}

                .highlight {{ font-weight: bold; color: #0277bd; }}
                .notes-box {{ background-color: #fffde7; padding: 8px; border: 1px solid #fff9c4; margin-top: 5px; white-space: pre-wrap; }}

                .out-of-range {{ color: #d32f2f; font-weight: bold; }}
                .in-range {{ color: #2e7d32; }}

                .bar-container {{ background-color: #f0f0f0; height: 12px; width: 100%; border-radius: 2px; }}
                .bar-fill {{ background-color: #1976d2; height: 100%; border-radius: 2px; }}
            </style>
        </head>
        <body>
            <!-- Letterhead Header -->
            <table class="header-table">
                <tr>
                    <td style="border:none; vertical-align: bottom;">
                        <div class="company-name">🌿 {company_name if company_name else "Fire & Ice Apothecary"}</div>
                        <div class="company-web">{website}</div>
                    </td>
                    <td style="border:none; vertical-align: bottom;">
                        <div class="report-title">{recipe_name}</div>
                        <div class="report-date">Date: {date_str}</div>
                    </td>
                </tr>
            </table>
        """

        # Calculate true total weight early for display
        additive_weight = sum(self.calculator.additives.values())
        true_total_weight = props["total_batch_weight"] + additive_weight

        # --- Master Batch Logic ---
        water_row_label = "Water"
        water_val = props["water_weight"]
        lye_row_label = "Lye"
        lye_val = props["lye_weight"]
        html += f"""
            <!-- Top Section: Parameters and Totals Side-by-Side -->
            <table style="border:none; width:100%; margin-top:0;">
            <tr style="vertical-align:top;">
            <td style="width:48%; border:none; padding:0; padding-right:10px;">
                <div class="section-header" style="margin-top:0;">Batch Parameters</div>
                <table class="param-table">
                    <tr><td class="param-label">Total Oil Weight:</td><td>{self.calculator.convert_weight(props['total_oil_weight'], 'pounds'):.2f} lbs / {props['total_oil_weight']:.0f} g</td></tr>
                    <tr><td class="param-label">Water % of Oils:</td><td>{(props['water_weight'] / props['total_oil_weight'] * 100) if props['total_oil_weight'] else 0:.1f} %</td></tr>
                    <tr><td class="param-label">Super Fat:</td><td>{self.calculator.superfat_percent} %</td></tr>
                    <tr><td class="param-label">Lye Concentration:</td><td>{(props['lye_weight'] / (props['lye_weight'] + props['water_weight']) * 100) if (props['lye_weight'] + props['water_weight']) else 0:.1f} %</td></tr>
                    <tr><td class="param-label">Water : Lye Ratio:</td><td>{(props['water_weight'] / props['lye_weight']) if props['lye_weight'] else 0:.2f}:1</td></tr>
                    <tr><td class="param-label">Lye Type:</td><td>{self.calculator.lye_type}</td></tr>
                </table>
            </td>
            <td style="width:48%; border:none; padding:0;">
                <div class="section-header" style="margin-top:0;">Liquids & Totals</div>
                <table>
                    <tr><th class="left-align">Item</th><th>Pounds</th><th>Ounces</th><th>Grams</th></tr>
                    <tr><td class="left-align">{water_row_label}</td><td>{water_val/453.592:.2f}</td><td>{water_val/28.3495:.2f}</td><td>{water_val:.1f}</td></tr>
                    <tr><td class="left-align">{lye_row_label}</td><td>{lye_val/453.592:.2f}</td><td>{lye_val/28.3495:.2f}</td><td>{lye_val:.1f}</td></tr>
                    <tr style="font-weight:bold;"><td class="left-align">Total Batch</td><td>{true_total_weight/453.592:.2f}</td><td>{true_total_weight/28.3495:.2f}</td><td>{true_total_weight:.1f}</td></tr>
                </table>
            </td>
            </tr>
            </table>

            <div class="section-header">Oils & Ingredients</div>
            <table>
                <tr><th class="left-align">Oil Name</th><th>%</th><th>Pounds</th><th>Ounces</th><th>Grams</th></tr>
        """

        total_oil = props["total_oil_weight"]
        for name, weight in self.calculator.oils.items():
            pct = (weight / total_oil * 100) if total_oil > 0 else 0
            html += f"<tr><td class='left-align'>{name}</td><td>{pct:.1f}</td><td>{weight/453.592:.3f}</td><td>{weight/28.3495:.2f}</td><td>{weight:.2f}</td></tr>"

        html += f"""
                <tr style="font-weight:bold; background-color:#fafafa;"><td class="left-align">Totals</td><td>100.0</td><td>{total_oil/453.592:.3f}</td><td>{total_oil/28.3495:.2f}</td><td>{total_oil:.2f}</td></tr>
            </table>
        """

        if self.calculator.additives:
            html += """
            <div class="section-header">Additives</div>
            <table>
                <tr><th class="left-align">Additive</th><th>Pounds</th><th>Ounces</th><th>Grams</th></tr>
            """
            for name, weight in self.calculator.additives.items():
                html += f"<tr><td class='left-align'>{name}</td><td>{weight/453.592:.3f}</td><td>{weight/28.3495:.2f}</td><td>{weight:.2f}</td></tr>"
            html += "</table>"

        # Two-column layout for Qualities and FA
        html += """
        <table style="border: none; margin-top: 20px;">
            <tr style="vertical-align: top;">
                <td style="width: 48%; border: none; padding: 0; padding-right: 10px;">
                    <div class="section-header" style="margin-top: 0;">Soap Qualities</div>
                    <table>
                        <tr><th class="left-align">Quality</th><th>Range</th><th>Value</th></tr>
        """

        for name, min_val, max_val in quality_ranges:
            val = int(round(qualities.get(name.lower(), 0)))
            style_class = (
                "out-of-range" if (val < min_val or val > max_val) else "in-range"
            )
            html += f"<tr><td class='left-align'>{name}</td><td>{min_val} - {max_val}</td><td class='{style_class}'>{val}</td></tr>"

        html += """
                    </table>
                </td>
                <td style="width: 4%; border: none;"></td>
                <td style="width: 48%; border: none; padding: 0;">
                    <div class="section-header" style="margin-top: 0;">Fatty Acid Profile</div>
                    <table>
                        <tr><th class="left-align">Acid</th><th>%</th></tr>
        """

        fa_order = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "ricinoleic",
            "oleic",
            "linoleic",
            "linolenic",
        ]
        for fa in fa_order:
            val = float(fa_profile.get(fa, 0.0))
            if val > 0.1:  # Only show present FAs
                html += f"""
                <tr>
                    <td class='left-align'>{fa.capitalize()}</td>
                    <td>{val:.1f}%</td>
                </tr>
                """

        html += """
                    </table>
                </td>
            </tr>
        </table>
        """

        html += label_html

        if notes:
            html += f"<div class='section-header'>Instructions & Notes</div><div class='notes-box'>{notes}</div>"

        html += "</body></html>"
        self.viewer.setHtml(html)

    def generate_label_html(self, props):
        """Generate INCI label preview"""
        # Determine salt prefix based on lye
        lye_type = self.calculator.lye_type
        prefix = "Potassium" if "KOH" in lye_type else "Sodium"

        # Common INCI root mapping
        # This maps the oil name to the root used with Sodium/Potassium
        inci_roots = {
            "Olive Oil": "Olivate",
            "Coconut Oil": "Cocoate",
            "Palm Oil": "Palmate",
            "Castor Oil": "Castorate",
            "Sweet Almond Oil": "Sweet Almondate",
            "Avocado Oil": "Avocadoate",
            "Shea Butter": "Shea Butterate",
            "Cocoa Butter": "Cocoa Butterate",
            "Lard": "Lardate",
            "Tallow": "Tallowate",
            "Babassu Oil": "Babassuate",
            "Sunflower Oil": "Sunflowerate",
            "Safflower Oil": "Safflowerate",
            "Rice Bran Oil": "Rice Branate",
            "Mango Seed Butter": "Mango Butterate",
            "Hemp Oil": "Hempseedate",
            "Neem Seed Oil": "Neemate",
            "Stearic Acid": "Stearate",
        }

        # Collect all ingredients with weights
        ingredients = []

        # Oils (converted to salts)
        for name, weight in self.calculator.oils.items():
            # Check if we have a mapping
            root = inci_roots.get(name)
            if root:
                inci_name = f"{prefix} {root}"
            else:
                # Fallback for unmapped oils
                inci_name = f"Saponified {name}"
            ingredients.append((weight, inci_name))

        # Additives
        for name, weight in self.calculator.additives.items():
            # Simple mapping for common additives
            if "Fragrance" in name or "EO" in name:
                ingredients.append((weight, "Parfum (Fragrance)"))
            else:
                ingredients.append((weight, name))

        # Water (Aqua) and Glycerin
        # Note: In a finished bar, much water evaporates, but Glycerin is produced.
        # This is an estimation. Glycerin is roughly ~10% of oil weight in cold process.
        # Water remaining is variable, but we'll list Aqua based on input water for the raw list order,
        # or place it appropriately. Standard INCI lists Aqua often 1st or 2nd.
        # For simplicity in this generator, we will add Aqua and Glycerin based on batch proportions.

        ingredients.append((props["water_weight"], "Aqua"))
        ingredients.append(
            (props["total_oil_weight"] * 0.1, "Glycerin")
        )  # Rough estimate

        # Sort by weight descending
        ingredients.sort(key=lambda x: x[0], reverse=True)

        # Format list
        label_text = ", ".join([item[1] for item in ingredients])

        return f"""
        <div class="section-header">Ingredient Label (INCI Preview)</div>
        <div style="padding: 8px; border: 1px dashed #999; background-color: #f9f9f9; margin-top: 5px; font-size: 10px;">
            <b>Ingredients:</b> {label_text}
        </div>
        <div style="font-size: 11px; color: #666; margin-top: 5px;">* Generated estimation. Verify with local regulations.</div>
        """

    def print_report(self):
        if not _HAS_PRINTER:
            return

        # Use ScreenResolution to fix tiny text issue in PDFs
        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)

        preview = QPrintPreviewDialog(printer, self)
        preview.setMinimumSize(1000, 800)
        preview.paintRequested.connect(lambda p: self.viewer.print(p))
        preview.exec()
