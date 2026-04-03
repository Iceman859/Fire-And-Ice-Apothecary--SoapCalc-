import os
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from src.utils.logger import log


class RecipeReportWidget(QWidget):
    """Luxury Report Engine - CSS styles handled externally in report_style.css"""

    def __init__(self, view, calculator):
        super().__init__()
        self.view = view
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Artisan Report")
        refresh_btn.setStyleSheet("""
            background-color: #3F4238; color: #C5A059;
            font-weight: bold; border: 1px solid #C5A059; padding: 8px 20px;
        """)
        refresh_btn.clicked.connect(lambda: self.refresh_report())
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.viewer = QWebEngineView()
        layout.addWidget(self.viewer)
        self.setLayout(layout)

    def refresh_report(self, recipe_name=None, notes=None, instructions=None):
            """Dynamic Luxury Report - Checks mode to display correct Phases"""
            # 1. SETUP & DATA
            recipe = self.view.current_recipe
            props = self.calculator.get_batch_properties()
            current_mode = self.view.get_current_mode()
            is_soap = (current_mode == "Cold Process Soap")
            base_path = os.path.dirname(os.path.abspath(__file__))
            sidebar_html = self._get_sidebar(props, is_soap)
            try:
                log.debug(f"Inside of Try Loop")
                # Get the current recipe object
                recipe = self.view.current_recipe
                # Pull the LIVE text from your widgets
                # Update these variable names to match your actual UI variables
                recipe.name = recipe.name or "Untitled Formulation"
                log.debug(f"Recipe Name: {recipe.name}")
                recipe.instructions = self.view.instructions
                log.debug(f"Recipe Instructions: {recipe.instructions}")
                recipe.notes = self.view.notes
                log.debug(f"Recipe Notes: {recipe.notes}")
                # Sync Scents as well
                recipe.scent_top = {
                    "name": recipe.scent_top_name.text(),
                    "description": recipe.scent_top_desc.text()
                }
                log.debug(f"Top Scent: {recipe.scent_top}")
                log.debug(f"Top Scent Description: {recipe.scent_top_desc.text()}")
            except:
                pass


            # 2. RENDER PHASE A (Always exists)
            oil_rows = ""
            for n, w in self.calculator.oils.items():
                perc = (w / props['total_oil_weight'] * 100) if props['total_oil_weight'] > 0 else 0
                oil_rows += f"<tr><td>{n}</td><td style='text-align:right'>{w:.2f}g</td><td style='text-align:right'>{perc:.1f}%</td></tr>"

            phase_a_html = f"""
            <div class="glass-card">
                <div class="phase-header sage">
                    <h2 style="font-family:'Playfair Display'; margin:0; font-style:italic">Phase A: Heat Phase</h2>
                    <span class="phase-badge">Oil Soluble</span>
                </div>
                <table class="data-table">
                    <thead><tr><th>Ingredient</th><th style='text-align:right'>Weight</th><th style='text-align:right'>%</th></tr></thead>
                    <tbody>{oil_rows}</tbody>
                </table>
            </div>"""

            # 3. RENDER PHASE B (Conditional: Lye for Soap, Cool Down for Body Products)
            phase_b_html = ""

            if is_soap:
                phase_b_html = f"""
                <div class="glass-card" style="margin-top: 2rem;">
                    <div class="phase-header charcoal">
                        <h2 style="font-family:'Playfair Display'; margin:0; font-style:italic">Phase B: Lye Solution</h2>
                        <span class="phase-badge">Reactive</span>
                    </div>
                    <table class="data-table">
                        <tr><td>Distilled Water</td><td style='text-align:right'>{props['water_weight']:.2f}g</td></tr>
                        <tr><td>{self.calculator.lye_type} Lye</td><td style='text-align:right'>{props['lye_weight']:.2f}g</td></tr>
                    </table>
                </div>"""
            else:
                # If it's a Body Product, we can display the Cool Down phase additives here
                # (Assuming you have a way to pull fragrance/extract weights)
                phase_b_html = f"""
                <div class="glass-card" style="margin-top: 2rem;">
                    <div class="phase-header charcoal">
                        <h2 style="font-family:'Playfair Display'; margin:0; font-style:italic">Phase B: Cool Down</h2>
                        <span class="phase-badge">Sensitive</span>
                    </div>
                    <div class="process-content" style="padding: 1.5rem;">
                        Additives, Fragrances, and Essential Oils are incorporated once temperature drops below 40°C.
                    </div>
                </div>"""

            # 4. ASSEMBLE FINAL HTML (Updated to include sidebar_html)
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <link rel="stylesheet" type="text/css" href="report_style.css">
            </head>
            <body>
                <header class="luxury-header">
                    <span class="brand-tag">Fire & Ice Apothecary • Artisan Formulator</span>
                    <h1 class="recipe-title">{recipe.name or "Untitled"}</h1>
                </header>

                <main class="report-container">
                    <div class="left-column">
                        {phase_a_html}
                        {phase_b_html}
                    </div>

                    <div class="right-column">
                        {sidebar_html}

                        <div class="glass-card" style="padding: 2rem; border-left: 4px solid var(--gold); margin-top: 2rem;">
                            <h3 class='scent-header'>Scent Profile</h3>
                            {self._get_static_scent_html("Top Note", recipe.scent_top, "Bright", 33)}
                            {self._get_static_scent_html("Mid Note", recipe.scent_mid, "Heart", 66)}
                            {self._get_static_scent_html("Base Note", recipe.scent_base, "Deep", 100)}
                        </div>

                        <div class="glass-card" style="padding: 2rem; margin-top: 2rem; border-left: 4px solid var(--gold);">
                            <h3 style="font-family:'Playfair Display'; margin-top:0">The Process</h3>
                            <div class="process-timeline">
                                <div class="step-item">
                                    <p class="step-text">{recipe.instructions}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </body>
            </html>
            """
            self.viewer.setHtml(html, baseUrl=QUrl.fromLocalFile(base_path + "/"))

    def _get_static_scent_html(self, label, data, mood, progress):
        if not data.get("name"): return ""
        return f"""
        <div class="scent-row">
            <div class="scent-meta">
                <span class="scent-label">{label}</span>
                <span class="scent-mood">{mood}</span>
            </div>
            <div class="progress-bg"><div class="progress-fill" style="width:{progress}%"></div></div>
            <p style="margin: 0.5rem 0 0.25rem 0; font-weight:600;">{data['name']}</p>
            <p style="margin:0; font-size:0.75rem; color:var(--sage); font-style:italic;">{data['description']}</p>
        </div>"""

    def _get_olfactory_profile_chart(self, top, mid, base):
        """Generates the Scent chart using structured data"""
        # Only show if at least one scent name is filled in
        if not any([top['name'], mid['name'], base['name']]):
            return ""

        return f"""
        <div class="perf-card" style="border-left: 4px solid #C5A059; margin-top: 20px;">
            <h4 style="font-family: 'Playfair Display', serif; color: #C5A059; font-size: 20px; margin-top:0; margin-bottom:20px;">Scent Profile</h4>

            {self._get_scent_row("Top Note", top['name'], top['description'], 33)}
            {self._get_scent_row("Middle Note", mid['name'], mid['description'], 66)}
            {self._get_scent_row("Base Note", base['name'], base['description'], 100)}
        </div>
        """

    def _get_scent_row(self, label, name, desc, progress):
        if not name: return ""

        # Determine mood adjective based on label
        adj = "Zesty & Fresh" if "Top" in label else "Floral & Fruity" if "Middle" in label else "Warm & Sensual"

        return f"""
        <div style="margin-bottom: 20px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span style="font-size:9px; text-transform:uppercase; font-weight:bold; color:#C5A059; letter-spacing:1px;">{label}</span>
                <span style="font-size:10px; color:#6B705C; font-style:italic;">{adj}</span>
            </div>
            <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{progress}%;"></div></div>
            <p style="margin: 8px 0 2px 0; font-weight:600; color:#3F4238; font-size:14px;">{name}</p>
            <p style="margin: 0; font-size:12px; color:#6B705C; font-style:italic; line-height:1.4;">{desc}</p>
        </div>
        """

    def _generate_soap_layout(self, props):
        oil_rows = "".join([f"<tr><td><b>{n}</b></td><td align='right'>{w:.1f}g</td></tr>" for n, w in self.calculator.oils.items()])
        return f"""
            <div class="phase-card">
                <div class="phase-header">Phase A: Saponifiables <span class="phase-badge">Oil Soluble</span></div>
                <table class="data-table">{oil_rows}</table>
            </div>
            <div class="phase-card">
                <div class="phase-header" style="background:#3F4238;">Phase B: Lye Solution <span class="phase-badge">Reactive</span></div>
                <table class="data-table">
                    <tr><td>Distilled Water</td><td align="right">{props['water_weight']:.1f}g</td></tr>
                    <tr><td>{self.calculator.lye_type} Lye</td><td align="right">{props['lye_weight']:.1f}g</td></tr>
                </table>
            </div>
        """

    def _generate_body_layout(self, props):
        oil_rows = "".join([f"<tr><td><b>{n}</b></td><td align='right'>{w:.1f}g</td></tr>" for n, w in self.calculator.oils.items()])
        return f"""
            <div class="phase-card">
                <div class="phase-header">Phase A: Heat Phase <span class="phase-badge">Oil Soluble</span></div>
                <table class="data-table">{oil_rows}</table>
            </div>
        """

    def _get_sidebar(self, props, is_soap):
        if not is_soap:
            return '<div class="perf-card" style="border-left: 4px solid var(--gold);"><h4 style="margin-top:0; font-family: \'Playfair Display\', serif;">Formulation Info</h4><p style="font-size:12px;">Body Product</p></div>'

        qualities = props.get("relative_qualities", {})
        perf_bars = ""
        for q, v in qualities.items():
            perf_bars += f"""
                <div class="stat-row">
                    <div class="stat-labels"><span>{q}</span><span>{round(v)}</span></div>
                    <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{v}%"></div></div>
                </div>"""
        return f'<div class="perf-card" style="border-left: 4px solid var(--gold);"><h4 style="margin-top:0; font-family: \'Playfair Display\', serif;">Soap Performance</h4>{perf_bars}</div>'

    def generate_label_html(self, props):
        prefix = "Potassium" if "KOH" in self.calculator.lye_type else "Sodium"
        ingredients = sorted([(w, f"{prefix} Saponified {n}") for n, w in self.calculator.oils.items()], reverse=True)
        label_text = ", ".join([item[1] for item in ingredients])
        return f"""
            <h4 style="margin-top:0; font-size:12px; text-transform:uppercase; color:#6B705C; letter-spacing:1px;">INCI Label Preview</h4>
            <p style="font-size:11px; line-height:1.6; color:#3F4238;"><b>INGREDIENTS:</b> {label_text}, Aqua, Glycerin.</p>
        """