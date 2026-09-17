import os

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
from config.configuration import Configuration
from gui.constants import (
    COMPILER_GROUPS,
    CODING_STANDARDS,
    STANDALONE_COMPILERS,
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
        self.imposter_log_path = self.create_line_widgets("Enter path for imposter log file", browse_type="file")
        self.json_compilation_database_path = self.create_line_widgets("Enter path for JSON compilation database", browse_type="file")
        self.project_lnt_name = self.create_line_widgets("Enter project .lnt name")
        self.output_file_path_folder = self.create_line_widgets("Enter path for output file", browse_type="folder")
        self.output_file_name = self.create_line_widgets("Enter output file name")

        self.pclp_path.textChanged.connect(self.validate_inputs)
        self.pclp_config_path.textChanged.connect(self.validate_inputs)
        self.compiler_binary.textChanged.connect(self.validate_inputs)
        self.lint_output_location.textChanged.connect(self.validate_inputs)
        self.output_file_path_folder.textChanged.connect(self.validate_inputs)

        # Combobox widgets
        self.prog_language = self.create_combobox_widget(["Select Language","C", "C++", "Mixed C/C++"])
        self.output_format = self.create_combobox_widget(["Select Output Format", "Text", "HTML", "XML", "SARIF"])

        self.prog_language.currentIndexChanged.connect(self.validate_inputs)
        self.output_format.currentIndexChanged.connect(self.validate_inputs)

        # Button widgets
        self.generate_button = self.create_generic_button_widget("Generate Configuration", function=self.on_button_clicked_generate_config, fixedWidth=True)
        self.generate_button.setEnabled(False)

    def create_menus(self):
        self.selected_compiler = None  # Initialize selected compiler variable
        self.compiler_button = self.create_generic_button_widget("Select Compiler")

        compiler_menu = QMenu("Compiler", self)

        for compiler in STANDALONE_COMPILERS:
            self.add_selection_action(compiler_menu, compiler)

        for group_name, compilers in COMPILER_GROUPS.items():
            compiler_group_menu = compiler_menu.addMenu(group_name)
            for compiler in compilers:
                self.add_selection_action(compiler_group_menu, compiler)

        self.compiler_button.setMenu(compiler_menu)

    # Function to create layouts for the GUI to unclutter the __init__ function.
    def create_layouts(self):
        self.pclp_layout = QVBoxLayout()
        self.compiler_layout = QVBoxLayout()
        self.options_layout = QVBoxLayout()
        self.project_layout = QVBoxLayout()
        self.analysis_layout = QVBoxLayout()

        self.create_pclp_tab()
        self.create_compiler_tab()
        self.create_options_tab()
        self.create_project_tab()
        self.create_analysis_tab()

        # Generate button layout is created separately to ensure it is added to the main layout correctly.
        generate_button_layout = QHBoxLayout()
        generate_button_layout.addStretch()  # Add stretch to push the button to the right
        generate_button_layout.addWidget(self.generate_button)
        generate_button_layout.addStretch()  # Add stretch to push the button to the right
        #self.compiler_layout.addRow(generate_button_layout)
        
        self.pclp_layout.addStretch()
        self.compiler_layout.addStretch()
        self.project_layout.addStretch()
        self.options_layout.addStretch()
        self.analysis_layout.addStretch()

        self.pclp_layout.addLayout(self.create_navigation_buttons(show_previous=False, show_next=True))
        self.compiler_layout.addLayout(self.create_navigation_buttons(show_previous=True, show_next=True))
        self.options_layout.addLayout(self.create_navigation_buttons(show_previous=True, show_next=True))
        self.project_layout.addLayout(self.create_navigation_buttons(show_previous=True, show_next=True))
        self.analysis_layout.addLayout(self.create_navigation_buttons(show_previous=True, show_next=False))
        self.analysis_layout.addLayout(generate_button_layout)

    # This function creates the tabs for the GUI, adding the previously created layouts to each tab.
    def create_tabs(self):
        self.tabs = QTabWidget()
        self.create_tab_widget("1. PCLP", self.pclp_layout)
        self.create_tab_widget("2. Compiler", self.compiler_layout)
        self.create_tab_widget("3. Options", self.options_layout)
        self.create_tab_widget("4. Project", self.project_layout)
        self.create_tab_widget("5. Analysis", self.analysis_layout)

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
        options_checkboxes_layout, self.code_std_checkboxes = self.create_checkboxes_widget(CODING_STANDARDS)
        standard_group = self.create_group_box("Coding Standard", options_checkboxes_layout)
        add_options_layout, self.add_options_list = self.create_list_widget(dialog_title="Add Additional Options", label_text="Enter additional option:")
        add_options_group = self.create_group_box("Additional Options", add_options_layout)
        self.options_file_name.setText("additional_options.lnt")

        options_layout.addWidget(standard_group)
        options_layout.addWidget(add_options_group)
        options_layout.addLayout(self.create_layout_row("Options File Name:", self.options_file_name))
        self.options_layout.addLayout(options_layout)

    def create_project_tab(self):
        inner_tabs = QTabWidget()
        project_layout = QVBoxLayout()

        cmd_line_tab = QWidget()
        cmd_line_layout = QVBoxLayout()
        cmd_line_layout.addLayout(self.create_layout_row("Imposter Log:", self.imposter_log_path, browse=True, is_folder=False))
        cmd_line_layout.addLayout(self.create_layout_row("Compiler JSON:", self.json_compilation_database_path, browse=True, is_folder=False))
        cmd_line_tab.setLayout(cmd_line_layout)

        ide_build_group = QGroupBox("IDE Build")
        include_flag = self.create_layout_row("Include Flag:", self.create_line_widgets("Enter include flag (e.g., -I)"))
        define_flag = self.create_layout_row("Define Flag:", self.create_line_widgets("Enter define flag (e.g., -D)"))
        parse_button = self.create_generic_button_widget("Parse Command Line", function=self.on_click_parse_command_line, fixedWidth=True)
        parse_button_layout = QHBoxLayout()
        parse_button_layout.addStretch()  # Add stretch to push the button to the right
        parse_button_layout.addWidget(parse_button)
        parse_button_layout.addStretch() 
        parse_command_line_layout = QHBoxLayout()
        parse_command_line_layout.addLayout(include_flag)
        parse_command_line_layout.addLayout(define_flag)

        ide_build_layout = QVBoxLayout()
        ide_build_layout.addLayout(parse_command_line_layout)
        ide_build_layout.addLayout(parse_button_layout)
        ide_build_group.setLayout(ide_build_layout)

        inner_tabs.addTab(cmd_line_tab, "Command Line")
        inner_tabs.addTab(ide_build_group, "IDE Build")

        extensions_layout = QHBoxLayout()
        c_ext_layout, self.c_ext_list = self.create_list_widget(dialog_title="Add C File Extensions", label_text="Enter additional C extensions:", items=[".c"])
        c_ext_group = self.create_group_box("C File Extensions", c_ext_layout)
        cpp_ext_layout, self.cpp_ext_list = self.create_list_widget(dialog_title="Add C++ File Extensions", label_text="Enter additional C++ extensions:", items=[".cpp", ".cxx", ".cc"])
        cpp_ext_group = self.create_group_box("C++ File Extensions", cpp_ext_layout)
        extensions_layout.addWidget(c_ext_group)
        extensions_layout.addWidget(cpp_ext_group)

        self.project_lnt_name.setText("project.lnt")
        project_lnt_name = self.create_layout_row("Project .lnt Name:", self.project_lnt_name)

        project_layout.addWidget(inner_tabs)
        project_layout.addLayout(extensions_layout)
        project_layout.addLayout(project_lnt_name)
        self.project_layout.addLayout(project_layout)

    def create_analysis_tab(self):
        analysis_layout = QVBoxLayout()
        output_layout = QVBoxLayout()

        output_layout.addLayout(self.create_layout_row("Output Format:", self.output_format))
        output_layout.addLayout(self.create_layout_row("Output File Path:", self.output_file_path_folder, browse=True, is_folder=True))
        output_layout.addLayout(self.create_layout_row("Output File Name:", self.output_file_name))
        output_group = self.create_group_box("Analysis Output", output_layout)

        analysis_layout.addWidget(output_group)
        self.analysis_layout.addLayout(analysis_layout)

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
    def create_generic_button_widget(self, placeholder_texts="", function=None, fixedWidth=False):
        button = QPushButton(placeholder_texts)
        if function is not None:
            button.clicked.connect(function)
        if fixedWidth:
            button.setFixedWidth(160)
        return button

    # This function creates a "Browse..." button that opens a file or folder dialog when clicked, depending on the is_folder parameter.
    def create_browse_button_widget(self, line_edit_widget, is_folder=True):
        button = QPushButton("Browse...")
        if is_folder:
            button.clicked.connect(lambda: self.browse_for_folder(line_edit_widget))
        else:
            button.clicked.connect(lambda: self.browse_for_file(line_edit_widget))
        return button

    # This function creates a QTabWidget for the GUI, setting its title and layout.
    def create_tab_widget(self, tab_name="", layout=None):
        tab_widget = QWidget()
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

    def create_list_widget(self, dialog_title="Add Item", label_text="Enter item:", items=None):
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

        if items:
            for item in items:
                options_list.addItem(item)

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
        config = self.build_configuration()
        print(config)

    def on_click_parse_command_line(self):
        # Empty for now
        return

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
        self.validate_inputs()

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

    def validate_inputs(self):
        valid = True
        if not os.path.isdir(self.pclp_path.text()):
            valid = False
        if not os.path.isfile(self.pclp_config_path.text()):
            valid = False
        if not os.path.isfile(self.compiler_binary.text()):
            valid = False
        if not os.path.isdir(self.lint_output_location.text()):
            valid = False
        if not os.path.isdir(self.output_file_path_folder.text()):
            valid = False
        if not self.selected_compiler:
            valid = False
        if self.prog_language == "Select Language":
            valid = False
        self.generate_button.setEnabled(valid)

    def build_configuration(self):
        return Configuration(
            pclp_path=self.pclp_path.text(),
            pclp_config_path=self.pclp_config_path.text(),
            prog_language=self.prog_language.currentText(),
            compiler_binary=self.compiler_binary.text(),
            lint_output_location=self.lint_output_location.text(),
            lint_output_name=self.lint_output_name.text(),
            additional_options=self.additional_options.text(),
            options_file_name=self.options_file_name.text(),
            selected_compiler=self.selected_compiler,
            code_standards=self.code_standards.text().split(","),
            imposter_log=self.imposter_log.text(),
            json_compilation_database=self.json_compilation_database.text(),
            include_flags=self.include_flags.text(),
            define_flags=self.define_flags.text(),
            project_lnt_name=self.project_lnt_name.text(),
            c_file_extensions=self.c_file_extensions.text().split(","),
            cpp_file_extensions=self.cpp_file_extensions.text().split(","),
            output_file_path_folder=self.output_file_path_folder.text(),
            output_file_name=self.output_file_name.text()
        )

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
def create_window():
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()

    app.exec()