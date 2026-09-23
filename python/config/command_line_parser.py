from dataclasses import dataclass


@dataclass
class ParsedCommandLine:
    includes: list[str]
    defines: list[str]

class CommandLineParser:
    def __init__(self, include_flag, define_flag):
        self.include_flag = include_flag
        self.define_flag = define_flag

    def parse(self, command_line):
        includes = []
        defines = []

        # Parsing goes here

        return ParsedCommandLine(
            includes=includes,
            defines=defines
        )