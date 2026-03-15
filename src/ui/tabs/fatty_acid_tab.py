"""Fatty Acid Breakdown tab for soap recipe details"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from src.models import SoapCalculator

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    _HAS_MATPLOTLIB = True
except Exception:
    FigureCanvas = None
    Figure = None
    _HAS_MATPLOTLIB = False


class FABreakdownWidget(QWidget):
    """Displays fatty-acid breakdown as table and chart"""

    def __init__(self, calculator: SoapCalculator = None):
        super().__init__()
        self.calculator = calculator
        self.setup_ui()

    def setup_ui(self):
        # Two-column layout: left = table, right = chart
        layout = QHBoxLayout()

        # FA Labels Group (left column)
        self.fa_group = QGroupBox("Fatty Acid Profile")
        fa_layout = QGridLayout()

        self.fa_labels = {}
        order = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "oleic",
            "linoleic",
            "linolenic",
            "ricinoleic",
        ]

        for i, key in enumerate(order):
            fa_layout.addWidget(QLabel(f"{key.capitalize()}:"), i, 0)
            val_lbl = QLabel("0.00%")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            fa_layout.addWidget(val_lbl, i, 1)
            self.fa_labels[key] = val_lbl

        self.fa_group.setLayout(fa_layout)
        layout.addWidget(self.fa_group, 1)

        # Chart area (matplotlib)
        chart_col = QVBoxLayout()
        if _HAS_MATPLOTLIB:
            self.figure = Figure(figsize=(4, 3))
            self.canvas = FigureCanvas(self.figure)
            chart_col.addWidget(self.canvas)
        else:
            chart_col.addWidget(QLabel("Install matplotlib to see chart."))

        layout.addLayout(chart_col, 2)
        self.setLayout(layout)

    def update_fa(self, properties: dict, unit_system: str = "grams"):
        """Update FA breakdown table and chart from properties dict"""
        fa = properties.get("fa_breakdown", {}) if properties else {}
        order = [
            "lauric",
            "myristic",
            "palmitic",
            "stearic",
            "oleic",
            "linoleic",
            "linolenic",
            "ricinoleic",
        ]

        values = []
        labels = []
        for key in order:
            # `fa` provided by calculator is already percent (0-100)
            val = float(fa.get(key, 0.0))
            labels.append(key.capitalize())
            values.append(val)

            if key in self.fa_labels:
                self.fa_labels[key].setText(f"{val:.2f}%")

        if _HAS_MATPLOTLIB:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.bar(labels, values, color="#0d47a1")
            ax.set_ylabel("%")
            ax.set_title("Fatty Acid Breakdown")
            # scale y-axis to percent range (0-100) with small padding
            max_val = max(values) if values else 0
            ymax = min(100, max(10, max_val * 1.15))
            ax.set_ylim(0, ymax)
            ax.set_yticks(range(0, int(ymax) + 1, max(1, int(ymax // 5))))
            ax.tick_params(axis="x", rotation=45)
            self.figure.tight_layout()
            self.canvas.draw()
