def _(lines, start, end):
    line_index = len(lines) - 1
    while(lines[line_index][2] == '-' and line_index > 0):
        line_index -= 1
    line_index += 1

    semicolon = ';'

    while (start != end):
        if semicolon is ';':
            if lines[-1][-2][-1][-1] is not ' ':
                semicolon = ''
        start -= 1
        lines.insert(line_index, [start, '}', semicolon])
        line_index += 1
        semicolon = ''
