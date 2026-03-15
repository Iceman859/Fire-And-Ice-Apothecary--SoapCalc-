"""Theme engine for Fire & Ice Apothecary."""

class ThemeManager:
    @staticmethod
    def get_styles(accent_color="#0d47a1", hover_color="#1565c0", pressed_color="#0a3d91"):
        """Returns the master stylesheet. You can edit design here once."""
        return f"""
        QMainWindow, QWidget {{ background-color: #1e1e1e; color: #e0e0e0; }}
        QLabel {{ color: #ffffff; }}

        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{
            background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #3d3d3d;
            padding: 5px; border-radius: 3px;
        }}
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
            border: 1px solid {accent_color}; background-color: #323232;
        }}

        QPushButton {{
            background-color: {accent_color}; color: #e0e0e0; border: none;
            padding: 8px 16px; border-radius: 3px; font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {hover_color}; }}
        QPushButton:pressed {{ background-color: {pressed_color}; }}

        QTableWidget {{
            background-color: #2b2b2b; alternate-background-color: #353535;
            gridline-color: #444; color: #00BFFF; /* Ice Blue */
        }}
        QHeaderView::section {{
            background-color: #444; color: white; font-weight: bold;
            padding: 5px; border: 1px solid #3d3d3d;
        }}

        QTabWidget::pane {{ border: 1px solid #444; background: #252526; }}
        QTabBar::tab {{ background: #333; color: #ccc; padding: 10px 20px; border: 1px solid #444; }}
        QTabBar::tab:selected {{
            background-color: {accent_color};
            color: white;
            font-weight: bold;
        }}
        """

    @staticmethod
    def apply(widget, theme_name="Blue"):
        """Applies the selected theme to the provided widget."""
        themes = {
            "Blue": {"accent": "#0d47a1", "hover": "#1565c0", "pressed": "#0a3d91"},
            "Green": {"accent": "#2e7d32", "hover": "#388e3c", "pressed": "#1b5e20"},
            "Red": {"accent": "#c62828", "hover": "#d32f2f", "pressed": "#b71c1c"},
            "Purple": {"accent": "#6a1b9a", "hover": "#7b1fa2", "pressed": "#4a148c"},
            "Orange": {"accent": "#ef6c00", "hover": "#f57c00", "pressed": "#e65100"},
            "Teal": {"accent": "#00695c", "hover": "#00796b", "pressed": "#004d40"},
        }
        c = themes.get(theme_name, themes["Blue"])
        widget.setStyleSheet(ThemeManager.get_styles(c["accent"], c["hover"], c["pressed"]))