"""This task replaces empty C identifier lists "()" with "(void)"."""

import re

from wpiformat.task import Task


class CIdentList(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)
        file_changed = False

        output = ""
        pos = 0

        # C files use C linkage by default
        is_c = config_file.is_c_file(name)

        # Tokenize as extern "C" or extern "C++" with optional {, {, }, or ()
        # folllowed by { to disambiguate function calls. extern is first to try
        # matching a brace to it before classifying the brace as generic.
        extern_str = "(?P<ext_decl>extern \"C(\+\+)?\")\s+(?P<ext_brace>\{)?"
        token_regex = re.compile(extern_str + "|\{|\}|\(\)()(?=\s+\{)")

        EXTRA_POP_OFFSET = 2

        # If value is greater than pop offset, the value needs to be restored in
        # addition to an extra stack pop being performed. The pop offset is
        # removed before assigning to is_c.
        #
        # is_c + pop offset == 2: C lang restore that needs extra brace pop
        # is_c + pop offset == 3: C++ lang restore that needs extra brace pop
        extern_brace_indices = [is_c]

        for match in token_regex.finditer(lines):
            token = match.group()

            if token == "{":
                extern_brace_indices.append(is_c)
            elif token == "}":
                is_c = extern_brace_indices.pop()

                # If the next stack frame is from an extern without braces, pop
                # it.
                if extern_brace_indices[-1] >= EXTRA_POP_OFFSET:
                    is_c = extern_brace_indices[-1] - EXTRA_POP_OFFSET
                    extern_brace_indices.pop()
            elif token.startswith("extern"):
                # Back up language setting first
                if match.group("ext_brace"):
                    extern_brace_indices.append(is_c)
                else:
                    # Handling an extern without braces changing the language
                    # type is done by treating it as a pseudo-brace that gets
                    # popped as well when the next "}" is encountered.
                    # The "extra pop" offset is used as a flag on the top stack
                    # value that is checked whenever a pop is performed.
                    extern_brace_indices.append(is_c + EXTRA_POP_OFFSET)

                # Change language based on extern declaration
                if match.group("ext_decl") == "extern \"C\"":
                    is_c = True
                else:
                    is_c = False
            elif token == "()" and is_c:
                # Replaces () with (void)
                output += lines[pos:match.start()] + "(void)"
                pos += match.start() - pos + len("()")

                file_changed = True

        # Write rest of file if it wasn't all processed
        if pos < len(lines):
            output += lines[pos:]

        if file_changed:
            return (output, file_changed, True)
        else:
            return (lines, file_changed, True)
