import is_complete_line
import add_close_braces
import get_new_indent

def _(lines, line, indent):
    new_indent = get_new_indent._(line)
    if new_indent > indent + 1:
        lines.append([new_indent, line, '>'])
        return indent

    semicolon = ';' if is_complete_line._(line) else ''

    if new_indent == indent + 1:
        lines.append([indent, '{', ''])
        lines.append([new_indent, line, semicolon])
        return new_indent

    add_close_braces._(lines, indent, new_indent)
    indent = new_indent

    lines.append([indent, line, semicolon])

    return indent
