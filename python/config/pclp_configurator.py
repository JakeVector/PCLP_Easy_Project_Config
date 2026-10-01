import subprocess
import sys
from shutil import which
from config.configuration import Configuration
from gui.constants import CompilerInputSource
from gui.constants import OperatingSystem
from pathlib import Path

class PclpConfigurator:
    def __init__(self, config: Configuration):
        self.config = config

        if self.config.operating_system == OperatingSystem.WINDOWS.value:
            self.pclp_exe = Path(self.config.pclp_path) / "pclp64.exe"
        elif self.config.operating_system == OperatingSystem.LINUX.value:
            self.pclp_exe = Path(self.config.pclp_path) / "pclp64_linux"
        elif self.config.operating_system == OperatingSystem.MACOS.value:
            self.pclp_exe = Path(self.config.pclp_path) / "pclp64_macos"

        self.python_exe = (
            which("python")
            or which("python3")
        )
        if self.python_exe is None:
            raise EnvironmentError("Python executable not found.")

    def build_compiler_config(self):
        self.compiler_lnt_location = Path(self.config.lint_output_location) / f"{self.config.lint_output_name}"
        subprocess.run([self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                        f"--compiler-bin={self.config.compiler_binary}",
                        f"--config-output-lnt-file={self.compiler_lnt_location}.lnt",
                        f"--config-output-header-file={self.compiler_lnt_location}.h",
                        f"--compiler-options={self.config.additional_compiler_options}",
                        "--generate-compiler-config"])

    def build_options_file(self):
        if self.config.code_standards or self.config.additional_lint_options:
            self.options_file_location = Path(self.config.lint_output_location) / f"{self.config.options_file_name}"
            options_text = []

            for i, std in enumerate(self.config.code_standards):
                if i == 0:
                    options_text.append(f'-i"{self.config.pclp_path}/lnt"\n')
                options_text.append(f"{std}\n")

            for opt in self.config.additional_lint_options:
                options_text.append(f"{opt}\n")

            self.options_file_location.write_text("".join(options_text) + "\n")

    def build_project_config(self):
        self.project_lnt_location = Path(self.config.lint_output_location) / f"{self.config.project_lnt_name}"
        if self.config.compiler_input_src == CompilerInputSource.IMPOSTER:
            subprocess.run([self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                            f"--compiler-bin={self.config.compiler_binary}",
                            f"--imposter-file={self.config.imposter_log}",
                            f"--config-output-lnt-file={self.project_lnt_location}",
                            "--generate-project-config"])
        elif self.config.compiler_input_src == CompilerInputSource.JSON_COMPILATION_DATABASE:
            subprocess.run([self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                            f"--compiler-bin={self.config.compiler_binary}",
                            f"--compilation-db={self.config.json_compilation_database}",
                            f"--config-output-lnt-file={self.project_lnt_location}",
                            "--generate-project-config"])
        elif self.config.compiler_input_src == CompilerInputSource.COMMAND_LINE:
            project_file = self.project_lnt_location
            project_text = []
            for include in self.config.include_list:
                project_text.append(f'-i"{include}"\n')
            for define in self.config.define_list:
                project_text.append(f'-d{define}\n')
            for source in self.config.source_file_list:
                project_text.append(f"{source}\n")

            project_file.write_text("".join(project_text) + "\n")

    def run_analysis(self):
        if not Path(self.pclp_exe).exists():
            raise FileNotFoundError(f"PC-lint Plus executable not found at {self.pclp_exe}")
        else:
            subprocess.run([str(self.pclp_exe), str(self.compiler_lnt_location), str(self.options_file_location), str(self.project_lnt_location)])
            
    def generate(self):
        self.build_compiler_config()
        self.build_options_file()
        self.build_project_config()
        self.run_analysis()