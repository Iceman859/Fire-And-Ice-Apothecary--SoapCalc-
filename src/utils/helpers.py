import os
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QDoubleSpinBox, QFileDialog
from bs4 import BeautifulSoup


class SelectAllSpinBox(QDoubleSpinBox):
    """SpinBox that selects all text on focus for easier data entry"""

    def focusInEvent(self, event):
        super().focusInEvent(event)
        # The singleShot(0) trick ensures the selection happens
        # AFTER the default focus event is finished.
        QTimer.singleShot(0, self.selectAll)