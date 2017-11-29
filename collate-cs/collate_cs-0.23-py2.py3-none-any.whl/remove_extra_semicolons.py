def _(lines):
    for line_number in range(len(lines) - 2):
        line = lines[line_number]
        start_of_next = lines[line_number + 1][1]
        if line[-1] == ";":
            if start_of_next == "{":
                line[-1] = ''
    return lines
