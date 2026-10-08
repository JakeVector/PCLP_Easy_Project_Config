import os
import subprocess
from shutil import which
from config.configuration import Configuration, save_config
from gui.constants import CompilerInputSource, OutputFormat
from gui.constants import OperatingSystem
from pathlib import Path

class PclpConfigurator:
    def __init__(self, config: Configuration):
        self.config = config
        self.script_text = []
        self.config_generated = False

        if self.config.operating_system == OperatingSystem.WINDOWS.value:
            self.pclp_exe = Path(self.config.pclp_path) / "pclp64.exe"
        elif self.config.operating_system == OperatingSystem.LINUX.value:
            self.pclp_exe = Path(self.config.pclp_path) / "pclp64_linux"
        elif self.config.operating_system == OperatingSystem.MACOS.value:
            self.pclp_exe = Path(self.config.pclp_path) / "pclp64_macos"

        if not Path(self.pclp_exe).exists():
            raise FileNotFoundError(f"PC-lint Plus executable not found at {self.pclp_exe}")

        self.python_exe = (
            which("python")
            or which("python3")
        )
        if self.python_exe is None:
            raise EnvironmentError("Python executable not found.")

    def run_command(self, command, description):
        try:
            return subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to run command: {description}\n\n"
                               f"Exit code: {e.returncode}\n\n"
                               f"{e.stderr or e.stdout}\n") from e
        except OSError as e:
            raise RuntimeError(f"Failed to run command: {description}\n\n"
                               f"OS error: {e}\n") from e

    def build_compiler_config(self):
        self.compiler_lnt_location = Path(self.config.lint_output_location) / f"{self.config.lint_output_name}"
        compile_config_command = [self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                                  f"--compiler-bin={self.config.compiler_binary}",
                                  f"--config-output-lnt-file={self.compiler_lnt_location}.lnt",
                                  f"--config-output-header-file={self.compiler_lnt_location}.h",
                                  f"--compiler-options={self.config.additional_compiler_options}",
                                  f"--generate-compiler-config"]
        self.script_text.append(" ".join(compile_config_command))
        self.run_command(compile_config_command, "Build compiler config")

    def build_options_file(self):
        options_text = []
        options_text.append(f'-i"{self.config.pclp_path}/lnt"\n')
        if self.config.code_standards or self.config.additional_lint_options:
            self.options_file_location = Path(self.config.lint_output_location) / f"{self.config.options_file_name}"

            for i, std in enumerate(self.config.code_standards):
                options_text.append(f"{std}\n")

            for opt in self.config.additional_lint_options:
                options_text.append(f"{opt}\n")

        self.options_file_location.write_text("".join(options_text) + "\n")

    def build_project_config(self):
        self.project_lnt_location = Path(self.config.lint_output_location) / f"{self.config.project_lnt_name}"
        if self.config.compiler_input_src == CompilerInputSource.IMPOSTER.value:
            imposter_command = [self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                               f"--compiler-bin={self.config.compiler_binary}",
                               f"--imposter-file={self.config.imposter_log}",
                               f"--config-output-lnt-file={self.project_lnt_location}",
                               "--generate-project-config"]
            self.run_command(imposter_command, "Build project config with Imposter")
            self.script_text.append(" ".join(imposter_command))
        elif self.config.compiler_input_src == CompilerInputSource.JSON_COMPILATION_DATABASE.value:
            json_command = [self.python_exe, str(self.config.pclp_config_path), f"--compiler={self.config.selected_compiler}",
                            f"--compiler-bin={self.config.compiler_binary}",
                            f"--compilation-db={self.config.json_compilation_database}",
                            f"--config-output-lnt-file={self.project_lnt_location}",
                            "--generate-project-config"]
            self.run_command(json_command, "Build project config with JSON")
            self.script_text.append(" ".join(json_command))
        elif self.config.compiler_input_src == CompilerInputSource.COMMAND_LINE.value:
            project_file = self.project_lnt_location
            project_text = []
            for include in self.config.include_list:
                project_text.append(f'-i"{include}"\n')
            for define in self.config.define_list:
                project_text.append(f'-d{define}\n')
            for source in self.config.source_file_list:
                project_text.append(f"{source}\n")

            project_file.write_text("".join(project_text) + "\n")

    def build_analysis_command(self):
        analysis_command = []
        sarif_conversion_command = []
        if self.config.output_format == OutputFormat.TEXT.value:
            analysis_command = [str(self.pclp_exe), str(self.compiler_lnt_location), str(self.options_file_location),
                           f"-os[{self.config.output_file_path_folder}\\{self.config.output_file_name}.{self.config.output_format}]",
                           str(self.project_lnt_location)]
        elif self.config.output_format == OutputFormat.HTML.value or self.config.output_format == OutputFormat.XML.value:
            analysis_command = [str(self.pclp_exe), str(self.compiler_lnt_location), str(self.options_file_location),
                                f"-os[{self.config.output_file_path_folder}\\{self.config.output_file_name}.{self.config.output_format}]",
                                f"env-{self.config.output_format}.lnt",
                                str(self.project_lnt_location)]
        elif self.config.output_format == OutputFormat.SARIF.value:
            xml_results_path = f"{self.config.output_file_path_folder}\\{self.config.output_file_name}.xml"
            dump_output_path = f"{self.config.output_file_path_folder}\\dump_output.xml"
            version_path = f"{self.config.output_file_path_folder}\\version.txt"
            analysis_command = [str(self.pclp_exe), 
                                f"-dump_messages(file={dump_output_path}, format=xml)",
                                f"-oe({version_path}) -version",
                                str(self.compiler_lnt_location), 
                                str(self.options_file_location),
                                f"-os[{xml_results_path}]", f"env-xml.lnt",
                                str(self.project_lnt_location)]
            sarif_conversion_command = [str(self.python_exe), f"config\\generate-reports.py", f"--input-xml", f"{xml_results_path}",
                                        f"--input-xml-descriptions", f"{dump_output_path}", f"--input-version", f"{version_path}",
                                        f"--output-sarif", f"{self.config.output_file_path_folder}\\{self.config.output_file_name}.{self.config.output_format}",
                                        f"--deduplicate", f"1"]
        self.script_text.append(" ".join(analysis_command))
        if self.config.output_format == OutputFormat.SARIF.value:
            self.script_text.append(" ".join(sarif_conversion_command))
        return analysis_command, sarif_conversion_command

    # No error checking here because PC-lint analysis may have non-zero exit codes even if the analysis is successful
    def run_analysis(self, analysis_command, sarif_conversion_command=None):
        if self.config_generated:
            subprocess.run(analysis_command)
            if self.config.output_format == OutputFormat.SARIF.value:
                subprocess.run(sarif_conversion_command)

    def create_script(self):
        if self.config.operating_system == OperatingSystem.WINDOWS.value:
            script_path = Path(self.config.output_file_path_folder) / f"{self.config.output_file_name}.bat"
            self.script_text.insert(0, "@echo off")
        elif self.config.operating_system in (OperatingSystem.LINUX.value, OperatingSystem.MACOS.value):
            script_path = Path(self.config.output_file_path_folder) / f"{self.config.output_file_name}.sh"
            self.script_text.insert(0, "#!/bin/bash")

        script_path.write_text("\n\n".join(self.script_text))
        if self.config.operating_system in (OperatingSystem.LINUX.value, OperatingSystem.MACOS.value):
            os.chmod(script_path, 0o755)
            
    def generate(self):
        save_config(self.config, f"{self.config.output_file_path_folder}\\pclp_config.json")
        self.build_compiler_config()
        self.build_options_file()
        self.build_project_config()
        self.build_analysis_command()
        self.create_script()
        self.config_generated = True