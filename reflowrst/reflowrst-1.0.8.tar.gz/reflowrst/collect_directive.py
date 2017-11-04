def collect_directive(lines, index):
    output = []
    output.append(lines[index])
    index += 1
    while index < len(lines):
        if not lines[index] == '' and not lines[index].startswith(' '):
            return '\n'.join(output), index
        else:
            output.append(lines[index])
            index += 1
    return '\n'.join(output), index
