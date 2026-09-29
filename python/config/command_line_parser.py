from dataclasses import dataclass
import shlex


@dataclass
class ParsedCommandLine:
    includes: list[str]
    defines: list[str]
    source_files: list[str]

class CommandLineParser:
    def __init__(self, include_flag, define_flag, file_extensions):
        self.include_flag = include_flag
        self.define_flag = define_flag
        self.file_extensions = file_extensions

    def parse(self, command_line):
        includes = []
        defines = []
        source_files = []

        return ParsedCommandLine(
            includes=includes,
            defines=defines,
            source_files=source_files
        )