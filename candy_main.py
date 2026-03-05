import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.models.candy_calculator import CandyCalculator

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create an instance of the CandyCalculator
    candy_calc = CandyCalculator()

    # Create the main window, passing the candy calculator and a new title
    window = MainWindow(
        calculator=candy_calc, app_title="Fire & Ice Confections - Gummy Calculator"
    )

    window.show()
    sys.exit(app.exec())
