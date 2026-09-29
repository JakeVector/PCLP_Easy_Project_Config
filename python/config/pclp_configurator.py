import subprocess
import sys
from shutil import which
from config.configuration import Configuration
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

    def generate(self):
        self.build_compiler_config()