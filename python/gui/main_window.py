from PySide6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QPushButton, 
    QLineEdit, 
    QLabel, 
    QComboBox,
    QVBoxLayout,
    QHBoxLayout
)
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

        # Creating widgets for the GUI
        # QLineEdit for entering the path to PC-lint Plus, QComboBox for selecting the compiler family, 
        # and QPushButton for generating the configuration.
        self.pclp_path = QLineEdit(self)
        self.pclp_path.setPlaceholderText("Enter path to PC-lint Plus")

        self.compiler_family = QComboBox(self)
        self.compiler_family.addItems(["GCC", "Clang", "MSVC"])

        self.compiler_binary = QLineEdit(self)
        self.compiler_binary.setPlaceholderText("Enter compiler binary path")

        self.button = QPushButton("Generate Config")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.on_button_clicked)

        # Setting up GUI layout, VBoxLayout for vertical stacking and HBoxLayout for horizontal stacking of widgets
        layout = QVBoxLayout()

        pclp_path_layout = QHBoxLayout()
        pclp_path_layout.addWidget(QLabel("PC-lint Plus Path:"))
        pclp_path_layout.addWidget(self.pclp_path)
        layout.addLayout(pclp_path_layout)

        compiler_family_layout = QHBoxLayout()
        compiler_family_label = QLabel("Compiler Family:")
        compiler_family_label.setFixedWidth(90)  # Set a fixed width for the label to align with the input field
        compiler_family_layout.addWidget(compiler_family_label)
        compiler_family_layout.addWidget(self.compiler_family)
        layout.addLayout(compiler_family_layout)

        compiler_binary_layout = QHBoxLayout()
        compiler_binary_layout.addWidget(QLabel("Compiler Binary:"))
        compiler_binary_layout.addWidget(self.compiler_binary)
        layout.addLayout(compiler_binary_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)

    def on_button_clicked(self):
        print("Generate Config button clicked!")

def create_window():
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()

    app.exec()