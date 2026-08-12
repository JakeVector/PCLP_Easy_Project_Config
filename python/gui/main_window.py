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
        self.pclp_path = self.create_line_widgets("Enter path to PC-lint Plus")
        self.compiler_binary = self.create_line_widgets("Enter path to compiler executable")
        self.lint_output_location = self.create_line_widgets("Enter path for .lnt and .h files")
        self.lint_output_name = self.create_line_widgets("Enter file name for .lnt and .h files")
        
        self.create_combobox_widget()
        self.create_generate_button_widget()

        # Setting up GUI layout, VBoxLayout for vertical stacking and HBoxLayout for horizontal stacking of widgets
        self.create_layout()

    # This function creates QLineEdit widgets for entering the paths to PC-lint Plus, the compiler binary, and the lint output name.
    def create_line_widgets(self, placeholder_texts=""):
        line_edit_widget = QLineEdit(self)
        line_edit_widget.setPlaceholderText(placeholder_texts)
        return line_edit_widget

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
        
        layout.addRow(self.create_layout_row("PC-lint Plus Path:", self.pclp_path, browse=True, is_folder=True))
        layout.addRow(self.create_layout_row("Compiler Family:", self.compiler_family))
        layout.addRow(self.create_layout_row("Compiler Binary:", self.compiler_binary, browse=True, is_folder=False))
        layout.addRow(self.create_layout_row("Lint Output Location:", self.lint_output_location, browse=True, is_folder=True))
        layout.addRow(self.create_layout_row("Lint Output Name:", self.lint_output_name))

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

    def create_layout_row(self, label_text, widget, browse=False, is_folder=False):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(widget)
        if browse:
            if is_folder:
                layout.addWidget(self.create_browse_button_widget(widget, is_folder=True))
            else:
                layout.addWidget(self.create_browse_button_widget(widget, is_folder=False))
        return layout

def create_window():
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()

    app.exec()