def _(line):
    new_indent = 0
    for section in line:
        if (section != ''):
            break
        new_indent = new_indent + 1
    return new_indent
