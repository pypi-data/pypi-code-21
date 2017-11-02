def collect_footnote(lines, index):
    output = []
    output.append(lines[index])
    index += 1

    while index < len(lines):
        if (
          not lines[index] == '' and
          not is_footnote(lines, index)
        ):
            output.append(lines[index].lstrip())
            index += 1
        else:
            return ' '.join(output), index
    return ' '.join(output), index
