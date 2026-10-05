from config.configuration import Configuration
from config.pclp_configurator import PclpConfigurator
from config.command_line_parser import CommandLineParser

#def make_default_test_config(tmp_path, pclp_path, **overrides):
#    return config

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