from dataclasses import dataclass

@dataclass
class Configuration:
    operating_system: str
    pclp_path: str
    pclp_config_path: str
    prog_language: str
    compiler_binary: str
    lint_output_location: str
    lint_output_name: str
    additional_compiler_options: str
    options_file_name: str
    selected_compiler: str
    code_standards: list[str]
    additional_lint_options: list[str]
    imposter_log: str
    json_compilation_database: str
    include_flag: str
    define_flag: str
    project_lnt_name: str
    c_file_extensions: list[str]
    cpp_file_extensions: list[str]
    output_format: str
    output_file_path_folder: str
    output_file_name: str