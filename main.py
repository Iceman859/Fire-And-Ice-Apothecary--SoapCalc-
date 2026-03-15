"""Main application entry point"""

import sys
import os
from pathlib import Path
from src.utils.logger import log
# Ensure the project root is in the Python path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """Run the application"""
    log.info("App starting...")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
