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
    QCheckBox,
    QGroupBox,
    QListWidget,
    QGridLayout,
    QDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import QSize
import sys
from pathlib import Path
from gui.constants import (
    IAR_COMPILERS,
    KEIL_COMPILERS,
    HIGHTEC_COMPILERS,
    CCS_COMPILERS,
    S32DS_COMPILERS,
    MICROCHIP_COMPILERS,
    MVSC_COMPILERS,
    CODING_STANDARDS,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC-lint Plus Configurator")
        self.setFixedSize(QSize(650, 600))

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
        self.options_file_name = self.create_line_widgets("Enter file name for additional options (optional)")

        # Combobox widgets
        self.prog_language = self.create_combobox_widget(["Select Language","C", "C++", "Mixed C/C++"])

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

        self.add_selection_action(compiler_menu, "ghs")

        hightec_menu = compiler_menu.addMenu("HighTec")
        for compiler in HIGHTEC_COMPILERS:
            self.add_selection_action(hightec_menu, compiler)

        self.add_selection_action(compiler_menu, "tasking")

        ccs_menu = compiler_menu.addMenu("CCS")
        for compiler in CCS_COMPILERS:
            self.add_selection_action(ccs_menu, compiler)

        s32ds_menu = compiler_menu.addMenu("S32DS")
        for compiler in S32DS_COMPILERS:
            self.add_selection_action(s32ds_menu, compiler)

        microchip_menu = compiler_menu.addMenu("Microchip")
        for compiler in MICROCHIP_COMPILERS:
            self.add_selection_action(microchip_menu, compiler)

        mvsc_menu = compiler_menu.addMenu("MSVC")
        for compiler in MVSC_COMPILERS:
            self.add_selection_action(mvsc_menu, compiler)

        self.compiler_button.setMenu(compiler_menu)

    # Function to create layouts for the GUI to unclutter the __init__ function.
    def create_layouts(self):
        self.pclp_layout = QVBoxLayout()
        self.compiler_layout = QVBoxLayout()
        self.options_layout = QVBoxLayout()

        self.create_pclp_tab()
        self.create_compiler_tab()
        self.create_options_tab()

        # Generate button layout is created separately to ensure it is added to the main layout correctly.
        generate_button_layout = QHBoxLayout()
        generate_button_layout.addStretch()  # Add stretch to push the button to the right
        generate_button_layout.addWidget(self.button)
        generate_button_layout.addStretch()  # Add stretch to push the button to the right
        #self.compiler_layout.addRow(generate_button_layout)
        
        self.pclp_layout.addStretch()
        self.compiler_layout.addStretch() 
        self.pclp_layout.addLayout(self.create_navigation_buttons(show_previous=False, show_next=True))
        self.compiler_layout.addLayout(self.create_navigation_buttons(show_previous=True, show_next=True))
        self.options_layout.addLayout(self.create_navigation_buttons(show_previous=True, show_next=True))

    # This function creates the tabs for the GUI, adding the previously created layouts to each tab.
    def create_tabs(self):
        self.tabs = QTabWidget()
        self.create_tab_widget("1. PCLP", self.pclp_layout)
        self.create_tab_widget("2. Compiler", self.compiler_layout)
        self.create_tab_widget("3. Options", self.options_layout)

    # This function creates the main window layout, adding the tabs to the central widget of the QMainWindow.
    def create_window_layout(self):
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addWidget(self.tabs)
        container.setLayout(container_layout)

        self.setCentralWidget(container)

    def create_pclp_tab(self):
        pclp_layout = QVBoxLayout()
        pclp_paths_layout = QVBoxLayout()

        pclp_paths_layout.addLayout(self.create_layout_row("PC-lint Plus Path:", self.pclp_path, browse=True, is_folder=True))
        pclp_paths_layout.addLayout(self.create_layout_row("PC-lint Plus Config File:", self.pclp_config_path, browse=True, is_folder=False))
        pclp_paths_group = self.create_group_box("PC-lint Plus Paths", pclp_paths_layout)

        pclp_layout.addWidget(pclp_paths_group)
        pclp_layout.addLayout(self.create_layout_row("Programming Language:", self.prog_language))

        self.pclp_layout.addLayout(pclp_layout)

    def create_compiler_tab(self):
        compiler_layout = QVBoxLayout()
        compiler_info_layout = QVBoxLayout()
        lnt_files_layout = QVBoxLayout()

        compiler_info_layout.addLayout(self.create_layout_row("Compiler:", self.compiler_button))  # Add the button to the layout without a label
        compiler_info_layout.addLayout(self.create_layout_row("Compiler Binary:", self.compiler_binary, browse=True, is_folder=False))
        compiler_info_layout.addLayout(self.create_layout_row("Additional Options:", self.additional_options))
        compiler_info_group = self.create_group_box("Compiler", compiler_info_layout)

        lnt_files_layout.addLayout(self.create_layout_row("Lint Output Location:", self.lint_output_location, browse=True, is_folder=True))
        lnt_files_layout.addLayout(self.create_layout_row("Lint Output Name:", self.lint_output_name))
        lnt_files_group = self.create_group_box("Lint Output Files", lnt_files_layout)

        compiler_layout.addWidget(compiler_info_group)
        compiler_layout.addWidget(lnt_files_group)

        self.compiler_layout.addLayout(compiler_layout)

    def create_options_tab(self):
        options_layout = QVBoxLayout()
        options_checkboxes_layout, checkboxes = self.create_checkboxes_widget(CODING_STANDARDS)
        standard_group = self.create_group_box("Coding Standard", options_checkboxes_layout)
        add_options_layout, add_options_list = self.create_list_widget(dialog_title="Add Additional Options", label_text="Enter additional option:")
        add_options_group = self.create_group_box("Additional Options", add_options_layout)
        self.options_file_name.setText("additional_options.lnt")

        options_layout.addWidget(standard_group)
        options_layout.addWidget(add_options_group)
        options_layout.addLayout(self.create_layout_row("Options File Name:", self.options_file_name))
        self.options_layout.addLayout(options_layout)

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
        combo_box = QComboBox(self)
        combo_box.addItems(items)
        return combo_box

    # This function creates a QPushButton that is checkable and connects its clicked signal to the on_button_clicked function.
    def create_generic_button_widget(self, placeholder_texts="", function=None):
        button = QPushButton(placeholder_texts)
        button.setCheckable(True)
        if function is not None:
            button.clicked.connect(function)
        #button.setFixedWidth(160)  Useful for generate button which is not used currently
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

    # Create buttons to go to next or previous tab
    def create_navigation_buttons(self, show_previous=True, show_next=True):
        layout = QHBoxLayout()
        if show_previous:
            previous_button = QPushButton("Previous")
            previous_button.clicked.connect(self.go_to_previous_tab)
            layout.addWidget(previous_button)

        layout.addStretch()

        if show_next:
            next_button = QPushButton("Next")
            next_button.clicked.connect(self.go_to_next_tab)
            layout.addWidget(next_button)

        return layout

    def create_group_box(self, title, layout):
        group_box = QGroupBox(title)
        if layout is not None:
            group_box.setLayout(layout)
        return group_box

    def create_checkboxes_widget(self, options):
        checkboxes = []
        layout = QGridLayout()
        for i, option in enumerate(options):
            checkbox = QCheckBox(option)
            checkboxes.append(checkbox)
            layout.addWidget(checkbox, i // 4, i % 4)  # Arrange checkboxes in a grid with 3 columns
        return layout, checkboxes

    def create_list_widget(self, dialog_title="Add Item", label_text="Enter item:"):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        options_list = QListWidget()

        add_button = QPushButton("+")
        remove_button = QPushButton("-")
        add_button.setFixedSize(30, 30)
        remove_button.setFixedSize(30, 30)
        add_button.setStyleSheet("color: green; font-size: 18px; font-weight: bold;")
        remove_button.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")

        add_button.clicked.connect(lambda: self.add_item_to_list(dialog_title, label_text, options_list))
        remove_button.clicked.connect(lambda: self.remove_selected_item_from_list(options_list))

        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)

        layout.addLayout(button_layout)
        layout.addWidget(options_list)

        return layout, options_list

    def add_item_to_list(self, dialog_title="Add Item", label_text="Enter item:", options_list=None):
        dialog = QDialog(self)
        dialog.setWindowTitle(dialog_title)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(label_text))

        path_edit = QLineEdit()
        layout.addWidget(path_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            path = path_edit.text().strip()

            if path:
                options_list.addItem(path)

    def remove_selected_item_from_list(self, options_list):
        current_item = options_list.currentItem()

        if current_item:
            options_list.takeItem(
                options_list.row(current_item)
            )
    
    def go_to_next_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index < self.tabs.count() - 1:
            self.tabs.setCurrentIndex(current_index + 1)

    def go_to_previous_tab(self):
        current_index = self.tabs.currentIndex()

        if current_index > 0:
            self.tabs.setCurrentIndex(current_index - 1)

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

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
def create_window():
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()

    app.exec()