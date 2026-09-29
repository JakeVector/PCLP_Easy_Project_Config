from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
)
from config.command_line_parser import CommandLineParser

class CommandLineDialog(QDialog):
    def __init__(self, include_flag, define_flag, file_extensions, parent=None):
        super().__init__(parent)
        self.parsed_results = None
        self.include_flag = include_flag
        self.define_flag = define_flag
        self.file_extensions = file_extensions

        self.setWindowTitle("Parse Command Line")
        self.setMinimumWidth(600)

        self.command_line = QLineEdit()
        self.command_line.setPlaceholderText(
            "Enter compiler command line..."
        )

        self.parse_button = QPushButton("Parse")
        self.apply_button = QPushButton("Apply")
        self.apply_button.setEnabled(False)
        self.cancel_button = QPushButton("Cancel")

        self.includes_list = QListWidget()
        self.defines_list = QListWidget()
        self.source_files_list = QListWidget()

        self.parse_button.clicked.connect(self.parse_command_line)
        self.apply_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.create_layout()

    def create_layout(self):
        main_layout = QVBoxLayout(self)
        results_layout = QHBoxLayout()
        include_layout = QVBoxLayout()
        define_layout = QVBoxLayout()
        source_layout = QVBoxLayout()

        # Command line input
        main_layout.addWidget(QLabel("Command Line:"))
        main_layout.addWidget(self.command_line)

        # Parse button
        parse_layout = QHBoxLayout()
        parse_layout.addStretch()
        parse_layout.addWidget(self.parse_button)

        main_layout.addLayout(parse_layout)

        # Parsed include paths
        include_layout.addWidget(QLabel("Includes:"))
        include_layout.addWidget(self.includes_list)

        # Parsed defines
        define_layout.addWidget(QLabel("Defines:"))
        define_layout.addWidget(self.defines_list)

        source_layout.addWidget(QLabel("Source Files:"))
        source_layout.addWidget(self.source_files_list)

        # Apply / Cancel buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)

        results_layout.addLayout(include_layout)
        results_layout.addLayout(define_layout)
        results_layout.addLayout(source_layout)

        main_layout.addLayout(results_layout)
        main_layout.addLayout(button_layout)

    def parse_command_line(self):
        # Empty for now
        parser = CommandLineParser(self.include_flag, self.define_flag, self.file_extensions)
        result = parser.parse(self.command_line.text())
        self.includes_list.clear()
        self.defines_list.clear()
        self.source_files_list.clear()
        self.includes_list.addItems(result.includes)
        self.defines_list.addItems(result.defines)
        self.source_files_list.addItems(result.source_files)

        self.parsed_results = result
        self.apply_button.setEnabled(True)