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

        self.layout = QFormLayout()

        # Creating widgets for the GUI
        # QLineEdit for entering the path to PC-lint Plus, QComboBox for selecting the compiler family, 
        # and QPushButton for generating the configuration.
        self.pclp_path = self.create_line_widgets("Enter path to PC-lint Plus")
        self.compiler_binary = self.create_line_widgets("Enter path to compiler executable")
        self.lint_output_location = self.create_line_widgets("Enter path for .lnt and .h files")
        self.lint_output_name = self.create_line_widgets("Enter file name for .lnt and .h files")
        self.compiler_family = self.create_combobox_widget(["GCC", "Clang", "MSVC"])
        # Creating a button for generating the configuration, which is connected to the on_button_clicked function.
        self.button = self.create_generic_button_widget("Generate Config", function=self.on_button_clicked)

        # Create layout for each row of widgets, including labels and browse buttons where applicable.
        pclp_path_layout = self.create_layout_row("PC-lint Plus Path:", self.pclp_path, browse=True, is_folder=True)
        compiler_family_layout = self.create_layout_row("Compiler Family:", self.compiler_family)
        compiler_binary_layout = self.create_layout_row("Compiler Binary:", self.compiler_binary, browse=True, is_folder=False)
        lint_output_location_layout = self.create_layout_row("Lint Output Location:", self.lint_output_location, browse=True, is_folder=True)
        lint_output_name_layout = self.create_layout_row("Lint Output Name:", self.lint_output_name)

        # Generate button layout is created separately to ensure it is added to the main layout correctly.
        generate_button_layout = QHBoxLayout()
        generate_button_layout.addStretch()  # Add stretch to push the button to the right
        generate_button_layout.addWidget(self.button)
        generate_button_layout.addStretch()  # Add stretch to push the button to the right

        # Setting up GUI layout, adding the widgets to the layout and setting the layout for the main window.
        self.layout.addRow(pclp_path_layout)
        self.layout.addRow(compiler_family_layout)
        self.layout.addRow(compiler_binary_layout)
        self.layout.addRow(lint_output_location_layout)
        self.layout.addRow(lint_output_name_layout)
        self.layout.addRow(generate_button_layout)  # Add the button layout to the main layout

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    # This function creates QLineEdit widgets for entering the paths to PC-lint Plus, the compiler binary, and the lint output name.
    def create_line_widgets(self, placeholder_texts=""):
        line_edit_widget = QLineEdit(self)
        line_edit_widget.setPlaceholderText(placeholder_texts)
        return line_edit_widget

    # This function creates a QComboBox for selecting the compiler family, with options for GCC, Clang, and MSVC.
    def create_combobox_widget(self, items=None):
        if items is None:
            return
        combo_box = QComboBox(self)
        combo_box.addItems(items)
        return combo_box

    # This function creates a QPushButton that is checkable and connects its clicked signal to the on_button_clicked function.
    def create_generic_button_widget(self, placeholder_texts="", function=None):
        button = QPushButton(placeholder_texts)
        button.setCheckable(True)
        if function is not None:
            button.clicked.connect(function)
        button.setFixedWidth(150)  # Set a fixed width for the button
        return button

    # This function creates a "Browse..." button that opens a file or folder dialog when clicked, depending on the is_folder parameter.
    def create_browse_button_widget(self, line_edit_widget, is_folder=True):
        if is_folder:
            button = QPushButton("Browse...")
            button.clicked.connect(lambda: self.browse_for_folder(line_edit_widget))
        else:
            button = QPushButton("Browse...")
            button.clicked.connect(lambda: self.browse_for_file(line_edit_widget))
        return button

    # This function creates a layout row that includes a label, a widget (like QLineEdit or QComboBox), and optionally a "Browse..." button.
    def create_layout_row(self, label_text="", widget=None, browse=False, is_folder=False):
            if widget is None:
                return
            layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(120)
            layout.addWidget(label)
            layout.addWidget(widget)
            if browse:
                layout.addWidget(self.create_browse_button_widget(widget, is_folder))
            return layout

    # This function is called when the "Generate Config" button is clicked. It currently prints a message to the console.
    def on_button_clicked(self):
        print("Generate Config button clicked!")

    # This function opens a folder selection dialog and sets the selected folder path to the provided QLineEdit widget.
    def browse_for_folder(self, line_edit_widget):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder_path:
            line_edit_widget.setText(folder_path)

    # This function opens a file selection dialog and sets the selected file path to the provided QLineEdit widget.
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