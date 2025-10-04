from PyQt6.QtWidgets import QApplication
from gui.debra_gui import DebraGUI
import sys

app = QApplication(sys.argv)
gui = DebraGUI()
gui.show()
sys.exit(app.exec())