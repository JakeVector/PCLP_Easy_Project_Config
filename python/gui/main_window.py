from PySide6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QPushButton, 
    QLineEdit, 
    QLabel, 
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QFormLayout
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
        self.setFixedSize(QSize(600, 200))

        # Creating widgets for the GUI
        # QLineEdit for entering the path to PC-lint Plus, QComboBox for selecting the compiler family, 
        # and QPushButton for generating the configuration.
        self.create_line_widgets()
        self.create_combobox_widget()
        self.create_generate_button_widget()

        # Setting up GUI layout, VBoxLayout for vertical stacking and HBoxLayout for horizontal stacking of widgets
        self.create_layout()

    # This function creates QLineEdit widgets for entering the paths to PC-lint Plus, the compiler binary, and the lint output name.
    def create_line_widgets(self):
        self.pclp_path = QLineEdit(self)
        self.pclp_path.setPlaceholderText("Enter path to PC-lint Plus")

        self.compiler_binary = QLineEdit(self)
        self.compiler_binary.setPlaceholderText("Enter path to compiler executable")

        self.lint_output_location = QLineEdit(self)
        self.lint_output_location.setPlaceholderText("Enter path for .lnt and .h files")
        
        self.lint_output_name = QLineEdit(self)
        self.lint_output_name.setPlaceholderText("Enter file name for .lnt and .h files")

    # This function creates a QComboBox for selecting the compiler family, with options for GCC, Clang, and MSVC.
    def create_combobox_widget(self):
        self.compiler_family = QComboBox(self)
        self.compiler_family.addItems(["GCC", "Clang", "MSVC"])

    # This function creates a QPushButton that is checkable and connects its clicked signal to the on_button_clicked function.
    def create_generate_button_widget(self):
        self.button = QPushButton("Generate Config")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.on_button_clicked)

    def create_browse_button_widget(self, line_edit_widget, is_folder=True):
        if is_folder:
            button = QPushButton("Browse...")
            button.clicked.connect(lambda: self.browse_for_folder(line_edit_widget))
        else:
            button = QPushButton("Browse...")
            button.clicked.connect(lambda: self.browse_for_file(line_edit_widget))
        return button

    # This function sets up the layout of the GUI, arranging the widgets in a vertical layout with horizontal layouts for each row of widgets.
    def create_layout(self):
        layout = QFormLayout()
        
        pclp_path_layout = QHBoxLayout()
        pclp_path_layout.addWidget(QLabel("PC-lint Plus Path:"))
        pclp_path_layout.addWidget(self.pclp_path)
        pclp_path_layout.addWidget(self.create_browse_button_widget(self.pclp_path, is_folder=True))
        layout.addRow(pclp_path_layout)

        compiler_family_layout = QHBoxLayout()
        compiler_family_label = QLabel("Compiler Family:")
        compiler_family_layout.addWidget(compiler_family_label)
        compiler_family_layout.addWidget(self.compiler_family)
        layout.addRow(compiler_family_layout)

        compiler_binary_layout = QHBoxLayout()
        compiler_binary_layout.addWidget(QLabel("Compiler Binary:"))
        compiler_binary_layout.addWidget(self.compiler_binary)
        compiler_binary_layout.addWidget(self.create_browse_button_widget(self.compiler_binary, is_folder=False))
        layout.addRow(compiler_binary_layout)

        lint_output_location_layout = QHBoxLayout()
        lint_output_location_layout.addWidget(QLabel("Lint Output Location:"))
        lint_output_location_layout.addWidget(self.lint_output_location)
        lint_output_location_layout.addWidget(self.create_browse_button_widget(self.lint_output_location, is_folder=True))
        layout.addRow(lint_output_location_layout)

        lint_output_name_layout = QHBoxLayout()
        lint_output_name_layout.addWidget(QLabel("Lint Output Name:"))
        lint_output_name_layout.addWidget(self.lint_output_name)
        layout.addRow(lint_output_name_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button)
        layout.addRow(button_layout)

        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)

    # This function is called when the "Generate Config" button is clicked. It currently prints a message to the console.
    def on_button_clicked(self):
        print("Generate Config button clicked!")

    def browse_for_folder(self, line_edit_widget):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            line_edit_widget.setText(folder_path)

    def browse_for_file(self, line_edit_widget):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            line_edit_widget.setText(file_path)

def create_window():
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()

    app.exec()