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

        tokens = shlex.split(command_line, posix=True)

        i = 0

        while i < len(tokens):
            token = tokens[i]

            if token == self.include_flag:
                if i + 1 < len(tokens):
                    includes.append(tokens[i + 1])
                    i += 1

            elif token.startswith(self.include_flag):
                includes.append(
                    token[len(self.include_flag):]
                )

            elif token == self.define_flag:
                if i + 1 < len(tokens):
                    defines.append(tokens[i + 1])
                    i += 1

            elif token.startswith(self.define_flag):
                defines.append(
                    token[len(self.define_flag):]
                )

            elif any(
                token.endswith(extension)
                for extension in self.file_extensions
            ):
                source_files.append(token)

            i += 1

        return ParsedCommandLine(
            includes=includes,
            defines=defines,
            source_files=source_files
        )