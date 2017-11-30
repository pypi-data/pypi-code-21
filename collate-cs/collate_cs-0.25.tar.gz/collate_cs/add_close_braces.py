def _(lines, start, end):
    line_index = len(lines) - 1
    while(lines[line_index][2] == '-' and line_index > 0):
        line_index -= 1
    line_index += 1

    while (start != end):
        start -= 1
        lines.insert(line_index, [start, '}', ''])
        line_index += 1
