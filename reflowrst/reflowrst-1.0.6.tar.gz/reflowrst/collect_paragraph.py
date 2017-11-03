def collect_paragraph(lines, index):
    output = [lines[index]]
    index += 1
    
    while index < len(lines):
        if not lines[index] == '':
            output.append(lines[index].strip())
            index += 1
        else:
            return ' '.join(output), index
    return ' '.join(output), index
