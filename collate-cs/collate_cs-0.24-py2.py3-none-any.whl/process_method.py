import add_close_braces
import process_line
import join_lines
import finish_semicolons
import remove_extra_semicolons

def _(src):
    raw_lines = src.split("\n")[0:-1]
    indent = 0

    lines = [[0,'','-']]
    for line in raw_lines:
        line = line.split('    ')
        indent = process_line._(lines, line, indent)
    add_close_braces._(lines, indent, 0)
    remove_extra_semicolons._(lines)

    return join_lines._(finish_semicolons._(lines[1:]))
