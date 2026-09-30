import subprocess
import sys
from shutil import which
from config.configuration import Configuration
from gui.constants import CompilerInputSource
from pathlib import Path

class PclpConfigurator:
    def __init__(self, config: Configuration):
        self.config = config

        self.python_exe = (
            which("python")
            or which("python3")
        )
        if self.python_exe is None:
            raise EnvironmentError("Python executable not found.")

    def build_compiler_config(self):
        subprocess.run([self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                        f"--compiler-bin={self.config.compiler_binary}",
                        f"--config-output-lnt-file={self.config.lint_output_location}/{self.config.lint_output_name}.lnt",
                        f"--config-output-header-file={self.config.lint_output_location}/{self.config.lint_output_name}.h",
                        f"--compiler-options={self.config.additional_compiler_options}",
                        "--generate-compiler-config"])

    def build_options_file(self):
        if self.config.code_standards or self.config.additional_lint_options:
            options_file = Path(self.config.lint_output_location) / f"{self.config.options_file_name}"
            options_text = []

            for i, std in enumerate(self.config.code_standards):
                if i == 0:
                    options_text.append(f'-i"{self.config.pclp_path}/lnt"\n')
                options_text.append(f"{std}\n")

            for opt in self.config.additional_lint_options:
                options_text.append(f"{opt}\n")

            options_file.write_text("".join(options_text) + "\n")

    def build_project_config(self):
        if self.config.compiler_input_src == CompilerInputSource.IMPOSTER:
            subprocess.run([self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                            f"--compiler-bin={self.config.compiler_binary}",
                            f"--imposter-file={self.config.imposter_log}",
                            f"--config-output-lnt-file={self.config.project_lnt_name}",
                            "--generate-project-config"])
        elif self.config.compiler_input_src == CompilerInputSource.JSON_COMPILATION_DATABASE:
            subprocess.run([self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                            f"--compiler-bin={self.config.compiler_binary}",
                            f"--compilation-db={self.config.json_compilation_database}",
                            f"--config-output-lnt-file={self.config.project_lnt_name}",
                            "--generate-project-config"])
        elif self.config.compiler_input_src == CompilerInputSource.COMMAND_LINE:
            project_file = Path(self.config.lint_output_location) / f"{self.config.project_lnt_name}"
            project_text = []
            for include in self.config.include_list:
                project_text.append(f'-i"{include}"\n')
            for define in self.config.define_list:
                project_text.append(f'-d{define}\n')
            for source in self.config.source_files:
                project_text.append(f"{source}\n")

            project_file.write_text("".join(project_text) + "\n")

    def generate(self):
        self.build_compiler_config()
        self.build_options_file()
        self.build_project_config()