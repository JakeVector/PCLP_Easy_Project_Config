from PySide6.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QPushButton, 
    QLineEdit, 
    QLabel, 
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QFileDialog,
    QTabWidget,
    QMenu,
    QPushButton,
)
from PySide6.QtCore import QSize
import sys
from pathlib import Path

IAR_COMPILERS = [
        "iar-430",
        "iar-78k",
        "iar-8051",
        "iar-arm",
        "iar-avr",
        "iar-avr32",
        "iar-cf",
        "iar-cr16c",
        "iar-h8",
        "iar-hcs12",
        "iar-m16c",
        "iar-m32c",
        "iar-maxq",
        "iar-r32c",
        "iar-rh850",
        "iar-r178",
        "iar-rx",
        "iar-s08",
        "iar-sam8",
        "iar-v850",
        ]

KEIL_COMPILERS = [
        "keil_armcc",
        "keil_armclang",
        "keil_c51",
        ]

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC-lint Plus Configurator")
        self.setFixedSize(QSize(650, 300))

        # Creating widgets for the GUI
        self.create_widgets()
        # Creating menus for the GUI
        self.create_menus()
        # Creating layouts for the GUI
        self.create_layouts()
        # Creating tabs for the GUI
        self.create_tabs()
        # Creating the main window layout
        self.create_window_layout()
        
    # Function to create widgets for the GUI to unclutter the __init__ function.
    def create_widgets(self):
        # LineEdit widgets
        self.pclp_path = self.create_line_widgets("Enter path to PC-lint Plus", browse_type="folder")
        self.pclp_config_path = self.create_line_widgets("Enter path to PC-lint Plus config file", browse_type="file")
        self.compiler_binary = self.create_line_widgets("Enter path to compiler executable", browse_type="file")
        self.lint_output_location = self.create_line_widgets("Enter path for .lnt and .h files", browse_type="folder")
        self.lint_output_name = self.create_line_widgets("Enter file name for .lnt and .h files")
        self.additional_options = self.create_line_widgets("Enter additional compiler options (optional)")

        # Combobox widgets
        self.prog_language = self.create_combobox_widget(["C", "C++", "Mixed C/C++"])

        # Button widgets
        self.button = self.create_generic_button_widget("Generate Compiler Config", function=self.on_button_clicked_generate_config)

    def create_menus(self):
        self.selected_compiler = None  # Initialize selected compiler variable
        self.compiler_button = self.create_generic_button_widget("Select Compiler")
        
        compiler_menu = QMenu("Compiler", self)

        self.add_selection_action(compiler_menu, "gcc")
        self.add_selection_action(compiler_menu, "clang")

        # IAR compilers are grouped under a submenu for better organization.
        iar_menu = compiler_menu.addMenu("IAR")       
        for compiler in IAR_COMPILERS:
            self.add_selection_action(iar_menu, compiler)
        
        keil_menu = compiler_menu.addMenu("Keil")
        for compiler in KEIL_COMPILERS:
            self.add_selection_action(keil_menu, compiler)

        self.add_selection_action(compiler_menu, "GHS")

        self.add_selection_action(compiler_menu, "msvc")
        self.compiler_button.setMenu(compiler_menu)

    # Function to create layouts for the GUI to unclutter the __init__ function.
    def create_layouts(self):
        self.pclp_layout = QFormLayout()
        self.compiler_layout = QFormLayout()

        # Create layout for each row of widgets, including labels and browse buttons where applicable.
        # Starting with the PC-lint Plus path and config file, followed by programming language selection for the first tab.
        self.pclp_layout.addRow(self.create_layout_row("PC-lint Plus Path:", self.pclp_path, browse=True, is_folder=True))
        self.pclp_layout.addRow(self.create_layout_row("PC-lint Plus Config File:", self.pclp_config_path, browse=True, is_folder=False))
        self.pclp_layout.addRow(self.create_layout_row("Programming Language:", self.prog_language))

        # Next tab has compiler family selection, compiler binary path, lint output location and name, and additional options and the config button.
        self.compiler_layout.addRow(self.create_layout_row("Compiler:", self.compiler_button))  # Add the button to the layout without a label
        self.compiler_layout.addRow(self.create_layout_row("Compiler Binary:", self.compiler_binary, browse=True, is_folder=False))
        self.compiler_layout.addRow(self.create_layout_row("Lint Output Location:", self.lint_output_location, browse=True, is_folder=True))
        self.compiler_layout.addRow(self.create_layout_row("Lint Output Name:", self.lint_output_name))
        self.compiler_layout.addRow(self.create_layout_row("Additional Options:", self.additional_options))

        # Generate button layout is created separately to ensure it is added to the main layout correctly.
        generate_button_layout = QHBoxLayout()
        generate_button_layout.addStretch()  # Add stretch to push the button to the right
        generate_button_layout.addWidget(self.button)
        generate_button_layout.addStretch()  # Add stretch to push the button to the right
        self.compiler_layout.addRow(generate_button_layout)

    # This function creates the tabs for the GUI, adding the previously created layouts to each tab.
    def create_tabs(self):
        self.tabs = QTabWidget()
        self.create_tab_widget("PCLP", self.pclp_layout)
        self.create_tab_widget("Compiler", self.compiler_layout)

    # This function creates the main window layout, adding the tabs to the central widget of the QMainWindow.
    def create_window_layout(self):
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addWidget(self.tabs)
        container.setLayout(container_layout)

        self.setCentralWidget(container)

    # This function creates QLineEdit widgets for entering the paths to PC-lint Plus, the compiler binary, and the lint output name.
    def create_line_widgets(self, placeholder_texts="", browse_type=None):
        line_edit_widget = QLineEdit(self)
        line_edit_widget.setPlaceholderText(placeholder_texts)

        if browse_type == "folder":
            line_edit_widget.textChanged.connect(lambda: self.validate_folder_path(line_edit_widget))
        elif browse_type == "file":
            line_edit_widget.textChanged.connect(lambda: self.validate_file_path(line_edit_widget))

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
        button.setFixedWidth(160)  # Set a fixed width for the button
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

    # This function creates a QTabWidget for the GUI, setting its title and layout.
    def create_tab_widget(self, tab_name="", layout=None):
        tab_widget = QTabWidget()
        tab_widget.setWindowTitle(tab_name)
        if layout is not None:
            tab_widget.setLayout(layout)
        self.tabs.addTab(tab_widget, tab_name)

    # This function creates a layout row that includes a label, a widget (like QLineEdit or QComboBox), and optionally a "Browse..." button.
    def create_layout_row(self, label_text="", widget=None, browse=False, is_folder=False):
            if widget is None:
                return
            layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFixedWidth(135)  # Set a fixed width for the label to align with other labels
            layout.addWidget(label)
            layout.addWidget(widget)
            if browse:
                layout.addWidget(self.create_browse_button_widget(widget, is_folder))
            return layout

    # This function is called when the "Generate Config" button is clicked. It currently prints a message to the console.
    def on_button_clicked_generate_config(self):
        pclp_path = self.pclp_path.text()
        pclp_config = self.pclp_config_path.text()
        language = self.prog_language.currentText()

        compiler_binary = self.compiler_binary.text()
        lint_output_location = self.lint_output_location.text()
        lint_output_name = self.lint_output_name.text()
        additional_options = self.additional_options.text()

        compiler_selection = self.selected_compiler if self.selected_compiler else "No compiler selected"
        

        print(pclp_path)
        print(pclp_config)
        print(language)
        print(compiler_binary)
        print(lint_output_location)
        print(lint_output_name)
        print(additional_options)
        print(compiler_selection)

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

    def add_selection_action(self, menu, text):
        action = menu.addAction(text)
        action.triggered.connect(
            lambda: self.select_compiler(text)
        )

    def select_compiler(self, compiler):
        self.selected_compiler = compiler
        self.compiler_button.setText(compiler)

    # This function validates the folder path entered in the dialog. If the path doesn't exist, the border turns red and a tooltip is displayed. If the path is valid, the border returns to normal and the tooltip is cleared.
    def validate_folder_path(self, line_edit_widget):
        folder_path = Path(line_edit_widget.text())
        if not folder_path.is_dir():
            line_edit_widget.setStyleSheet("border: 1px solid red;")
            line_edit_widget.setToolTip("Directory does not exist. Please enter a valid directory path.")
        else:
            line_edit_widget.setStyleSheet("")
            line_edit_widget.setToolTip("")

    # This function validates the file path entered in the dialog. If the path doesn't exist, the border turns red and a tooltip is displayed. If the path is valid, the border returns to normal and the tooltip is cleared.
    def validate_file_path(self, line_edit_widget):
        file_path = Path(line_edit_widget.text())
        if not file_path.is_file():
            line_edit_widget.setStyleSheet("border: 1px solid red;")
            line_edit_widget.setToolTip("File does not exist. Please enter a valid file path.")
        else:
            line_edit_widget.setStyleSheet("")
            line_edit_widget.setToolTip("")

def create_window():
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()

    app.exec()