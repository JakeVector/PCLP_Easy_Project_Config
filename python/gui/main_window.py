from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLineEdit, QLabel, QComboBox
from PySide6.QtCore import QSize, Qt
import sys

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC-lint Plus Configurator")
        self.setFixedSize(QSize(600, 600))

        button = QPushButton("Generate Config")
        button.setCheckable(True)
        button.clicked.connect(self.on_button_clicked)
        
        self.setCentralWidget(button)

    def on_button_clicked(self):
        print("Generate Config button clicked!")

def create_window():
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()

    app.exec()