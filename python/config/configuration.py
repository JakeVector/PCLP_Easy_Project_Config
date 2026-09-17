from dataclasses import dataclass

@dataclass
class Configuration:
    pclp_path: str
    pclp_config_path: str
    prog_language: str
    compiler_binary: str
    lint_output_location: str
    lint_output_name: str
    additional_options: str
    options_file_name: str
    selected_compiler: str
    code_standards: list[str]
    imposter_log: str
    json_compilation_database: str
    output_file_path_folder: str
    include_flags: str
    define_flags: str
    project_lnt_name: str
    c_file_extensions: list[str]
    cpp_file_extensions: list[str]
    output_file_name: str