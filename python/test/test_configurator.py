from config.configuration import Configuration
from config.pclp_configurator import PclpConfigurator
from config.command_line_parser import CommandLineParser
from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

TEST_OUTPUT = os.getenv("TEST_OUTPUT")
PCLINT_HOME = os.getenv("PCLINT_HOME")
MINGW_HOME = os.getenv("MINGW_HOME")

def test_command_line_parser():
    include_flag = "-I"
    define_flag = "-D"
    file_extensions = [".c", ".cpp", ".cc", ".cxx"]
    test_command_line = 'gcc -Wall -Wextra -O2 -I./include -I../common/include -I"C:\\SDK Files\\include" -DDEBUG -DVERSION=3 -DAPP_NAME="My Application" -DPLATFORM_WINDOWS src/main.c src/utils.cpp lib/helper.cc "src/test files/test.cxx" -std=c++20 -o build/application.exe'

    expected_includes = ["./include", "../common/include", "C:\\SDK Files\\include"]
    expected_defines = ["DEBUG", "VERSION=3", "APP_NAME=My Application", "PLATFORM_WINDOWS"]
    expected_files = ["src/main.c", "src/utils.cpp", "lib/helper.cc", "src/test files/test.cxx"]

    parser = CommandLineParser(include_flag=include_flag, define_flag=define_flag, file_extensions=file_extensions)
    result = parser.parse(test_command_line)

    assert result.includes == expected_includes
    assert result.defines == expected_defines
    assert result.source_files == expected_files

def test_pclp_configurator_initialization():
    # Mock configuration for testing
    config = Configuration(
        operating_system="Windows",
        pclp_path="C:/PCLint",
        pclp_config_path="C:/PCLint/config/pclp_config.py",
        prog_language="C++",
        selected_compiler="gcc",
        compiler_binary="C:/gcc/bin/gcc.exe",
        lint_output_location="C:/lint/output",
        lint_output_name="co-gcc",
        additional_compiler_options="-Wall -Wextra",
        options_file_name="additional_options.lnt",
        code_standards=["au-misra-cpp2.lnt"],
        additional_lint_options=["-max_threads=8"],
        imposter_log="C:/lint/imposter.log",
        json_compilation_database="C:/lint/compile_commands.json",
        parsed_command_line="",
        compiler_input_src="C:/src",
        include_list=["C:/include"],
        define_list=["DEBUG"],
        source_file_list=["C:/src/main.c"],
        c_ext_list=[".c"],
        cpp_ext_list=[".cpp"],
        project_lnt_name="project.lnt",
        output_format="xml",
        output_file_path_folder="C:/lint/output",
        output_file_name="lint_output"
    )
    configurator = PclpConfigurator(config)
    assert configurator.config == config

def test_generate_compiler_config():
    # Gennerate actual compiler configuration
    config = Configuration(
            operating_system="Windows",
            pclp_path=f"{PCLINT_HOME}",
            pclp_config_path=f"{PCLINT_HOME}/config/pclp_config.py",
            prog_language="C++",
            selected_compiler="gcc",
            compiler_binary=f"{MINGW_HOME}\\bin\\gcc.exe",
            lint_output_location=f"{TEST_OUTPUT}",
            lint_output_name="co-gcc",
            additional_compiler_options="-Wall -Wextra",
            options_file_name="additional_options.lnt",
            code_standards=["au-misra-cpp2.lnt"],
            additional_lint_options=["-max_threads=8"],
            imposter_log="C:/lint/imposter.log",
            json_compilation_database="C:/lint/compile_commands.json",
            parsed_command_line="",
            compiler_input_src="C:/src",
            include_list=["C:/include"],
            define_list=["DEBUG"],
            source_file_list=["C:/src/main.c"],
            c_ext_list=[".c"],
            cpp_ext_list=[".cpp"],
            project_lnt_name="project.lnt",
            output_format="xml",
            output_file_path_folder="C:/lint/output",
            output_file_name="lint_output"
        )
    configurator = PclpConfigurator(config)
    assert hasattr(configurator, 'build_compiler_config')
    assert callable(configurator.build_compiler_config)
    config_lnt_path = Path(f"{config.lint_output_location}") / f"{config.lint_output_name}.lnt"
    config_header_path = Path(f"{config.lint_output_location}") / f"{config.lint_output_name}.h"
    configurator.build_compiler_config()
    assert config_lnt_path.exists()
    assert config_header_path.exists()
