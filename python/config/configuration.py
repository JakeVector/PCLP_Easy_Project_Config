import json
from dataclasses import dataclass, asdict

@dataclass
class Configuration:
    operating_system: str
    pclp_path: str
    pclp_config_path: str
    prog_language: str
    selected_compiler: str
    compiler_binary: str
    lint_output_location: str
    lint_output_name: str
    additional_compiler_options: str
    options_file_name: str
    code_standards: list[str]
    additional_lint_options: list[str]
    imposter_log: str
    json_compilation_database: str
    parsed_command_line: str
    compiler_input_src: str
    include_list: list[str]
    define_list: list[str]
    source_file_list: list[str]
    c_ext_list: list[str]
    cpp_ext_list: list[str]
    project_lnt_name: str
    output_format: str
    output_file_path_folder: str
    output_file_name: str

def save_config(config: Configuration, file_path: str):
        with open(file_path, "w") as f:
            json.dump(asdict(config), f, indent=4)

def load_config(file_path: str) -> Configuration:
    with open(file_path, "r") as f:
        data = json.load(f)
    return Configuration(**data)