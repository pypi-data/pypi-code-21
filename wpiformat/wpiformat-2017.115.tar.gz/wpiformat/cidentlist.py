"""This task replaces empty C identifier lists "()" with "(void)"."""

import subprocess
import sys

from wpiformat.task import Task


class CIdentList(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        if config_file.is_c_file(name):
            token_regex = re.compile("\(\)")
        else:
            # Tokenize file as (), extern "C" {, {, or }
            token_regex = re.compile("\(\)|extern \"C\"\s+\{|\{|\}")

        brace_count = 0
        for match in token_regex.finditer(lines):
            token = match.group()

            if token == "{":
                brace_count += 1
            elif token == "}":
                brace_count -= 1
            elif token.startswith("using"):
                if brace_count == 0:
                    linenum = lines.count(linesep, 0, match.start()) + 1
                    if "NOLINT" not in lines.splitlines()[linenum - 1]:
                        format_succeeded = False
                        print(name + ": " + str(linenum) + ": '" + token + \
                              "' in global namespace")

        return (lines, False, format_succeeded)

        # Look in C files and within extern "C" of C++ files
        if config_file.is_c_file(name) or 
